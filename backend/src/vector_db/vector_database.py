import os
import logging
from pymilvus import MilvusClient, DataType
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "milvus_lite.db")
MILVUS_URI = os.environ.get("MILVUS_DB_PATH", _DEFAULT_DB_PATH)
COLLECTION_NAME = "services"
DENSE_DIM = 384  # BAAI/bge-small-en-v1.5 output dimension
SERVICES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "Services_description_V2.txt")

# Load embedding model once at startup
_model = SentenceTransformer("BAAI/bge-small-en-v1.5")

_client: MilvusClient | None = None


def _get_client() -> MilvusClient:
    global _client
    if _client is None:
        _client = MilvusClient(uri=MILVUS_URI)
    return _client


def _create_collection(client: MilvusClient) -> None:
    schema = client.create_schema(auto_id=True, enable_dynamic_field=False)
    schema.add_field("id", DataType.INT64, is_primary=True)
    schema.add_field("service_name", DataType.VARCHAR, max_length=256)
    schema.add_field("dense", DataType.FLOAT_VECTOR, dim=DENSE_DIM)

    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="dense",
        index_type="AUTOINDEX",  # Milvus Lite supports AUTOINDEX, FLAT, IVF_FLAT; full Milvus also supports HNSW
        metric_type="COSINE",
    )
    client.create_collection(COLLECTION_NAME, schema=schema, index_params=index_params)
    logger.info(f"Created Milvus collection '{COLLECTION_NAME}'")


def parse_services(file_content: str) -> list[tuple[str, str]]:
    services = []
    service_blocks = file_content.strip().split('---')
    for block in service_blocks:
        lines = block.strip().split('\n', 1)
        if len(lines) == 2:
            service_name = lines[0].strip()
            service_description = lines[1].strip().replace("\n", "")
            services.append((service_name, service_description))
    return services


def vector_db_push_batch(force_rebuild: bool = False) -> None:
    client = _get_client()

    if client.has_collection(COLLECTION_NAME):
        if not force_rebuild:
            stats = client.get_collection_stats(COLLECTION_NAME)
            if int(stats["row_count"]) > 0:
                logger.info(f"Collection '{COLLECTION_NAME}' already has {stats['row_count']} entities. Skipping index build.")
                return
        logger.warning(f"Dropping existing collection '{COLLECTION_NAME}' for rebuild.")
        client.drop_collection(COLLECTION_NAME)

    _create_collection(client)

    with open(SERVICES_FILE, encoding="utf-8") as f:
        services = parse_services(f.read())

    BATCH_SIZE = 64
    rows = []
    for i in tqdm(range(0, len(services), BATCH_SIZE), desc="Indexing services"):
        batch = services[i: i + BATCH_SIZE]
        texts = [f"{name} {desc}" for name, desc in batch]
        vecs = _model.encode(texts, normalize_embeddings=True).tolist()
        rows.extend(
            {"service_name": name, "dense": vec}
            for (name, _), vec in zip(batch, vecs)
        )

    client.insert(COLLECTION_NAME, data=rows)
    client.flush(COLLECTION_NAME)
    logger.info(f"Indexed {len(rows)} services into '{COLLECTION_NAME}'.")


def vector_search(user_query: str, limit: int = 3) -> list[str]:
    client = _get_client()
    q_vec = _model.encode([user_query], normalize_embeddings=True).tolist()
    results = client.search(
        collection_name=COLLECTION_NAME,
        data=q_vec,
        anns_field="dense",
        search_params={"metric_type": "COSINE", "params": {"ef": 100}},
        limit=limit,
        output_fields=["service_name"],
    )
    service_names = [hit["entity"]["service_name"] for hit in results[0]]
    logger.debug(f"vector_search('{user_query}', limit={limit}) -> {service_names}")
    return service_names
