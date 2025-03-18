
# IoT-Agentic Search Engine  

This repository contains the implementation of an IoT search engine integrated with the **SensorsConnect** framework. The **IoT-Agentic Search Engine** leverages **Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and an Agentic workflow** to enhance search capabilities.  

We have deployed this repository on a local machine for testing. You can try our demo using this [URL](https://iot-ase-demo-morning-brook-6041.fly.dev/IoT-ASE-Demo/chat).  

> **Note:** The current demo assumes the user's location is **downtown Toronto**.  
> If you want to query services in another location, make sure to **explicitly specify the location in your query**.  

## 🌍 Agentic Workflow Overview  

The **IoT-Agentic Search Engine** integrates three intelligent agents to retrieve and process information efficiently:  

### 1️⃣ IoT-RAG Search Engine  

- Retrieves data mimicking IoT-based information.  
- Hypothetically considers services around downtown Toronto, treating each service location as an IoT device.  
- For example, restaurants in the framework are considered IoT-integrated services, meaning each restaurant is treated as a virtual IoT device.  

### 2️⃣ Google Maps Agent  

- Handles uncovered zones or services by leveraging the **Google Maps API**.  
- If a relevant IoT service is not found in the **IoT-RAG Search Engine**, this agent searches for similar locations using **Google Maps**.  

### 3️⃣ Scraper Agent  

- Handles general queries or questions that cannot be answered by the other two agents.  
- Extracts relevant information by browsing web content.  

## 📌 Available Services  

Currently, the search engine provides recommendations for common **daily activities and services**, including:  

- 🛒 Grocery stores  
- 🏥 Walk-in clinics  
- 🚗 Car rental agencies  
- 🌳 Parks  
- 🍽️ Restaurants  
- ...and more (primarily places available on **Google Maps**).  

The **Agentic workflow** suggests places based on the following factors:  

- ⭐ **Reputation (Ratings)**  
- 🚗 **Real-time travel time** (using the **OpenRoute API**)  
- 👥 **Occupancy data** (scraped from **Google Maps** for crowd analysis)  

## 📝 Example Query  

Here’s how you can ask the **IoT-Agentic Search Engine** for a service recommendation:  

```plaintext
I want to have dinner with my family at a Middle Eastern restaurant with a good reputation.
```

This query will be processed by the Agentic workflow, and it will return results based on the available IoT data, Google Maps suggestions, and web-scraped information.

🚀 Feel free to try out our demo and explore the capabilities of the IoT-Agentic Search Engine!

## Installaion
This repository provides the IoT-Agentic-Search-Engine project that leverages a 
[DevContainer](https://code.visualstudio.com/docs/devcontainers/containers) for a seamless development environment setup. Follow the instructions below to install and start the demo.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1. **VS Code** - [Download and Install](https://code.visualstudio.com/)
2. **DevContainers Extension for VS Code**:
   - Install the [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) from the VS Code Extensions Marketplace.
3. **Docker** - [Download and Install](https://www.docker.com/products/docker-desktop/)

## Installation Steps

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/SensorsConnect/IoT-Agentic-Search-Engine.git
cd IoT-Agentic-Search-Engine
```

### 2. Open the Project in VS Code

Launch VS Code and open the cloned project directory:

```bash
code .
```

### 3. Reopen in DevContainer

1. Once the project is opened in VS Code, you'll see a prompt:  
   *"Folder contains a Dev Container configuration file. Reopen folder to develop in a container."*  
   Click **Reopen in Container**.

2. If the prompt does not appear, manually reopen the folder in a DevContainer:
   - Press `F1` (or `Ctrl+Shift+P`).
   - Select **Dev Containers: Reopen in Container**.

### 4. Build and Start the DevContainer

VS Code will automatically build the DevContainer using the provided `.devcontainer/devcontainer.json` file. This process may take a few minutes during the first run.

### 5. Activate IoT-Engine Conda Environment

1. Open a terminal inside the DevContainer.
2. Run the following command to activate the IoT-Engine Conda environment:

   ```bash
   conda activate IoT-engine
   ```

3. To make this environment the default for the container, run:

   ```bash
   conda config --set auto_activate_base false
   echo "conda activate IoT-engine" >> ~/.bashrc
   ```

4. Close and reopen the terminal to ensure the changes take effect.

VS Code will automatically build the DevContainer using the provided `.devcontainer/devcontainer.json` file. This process may take a few minutes during the first run.

### 5. Verify Setup

Once the container is running, verify that the environment is correctly set up by running the following command in the terminal inside the container:

```bash
bash setup-demo.sh
```

This script will install dependencies and prepare the demo.

### 6. Setting Up Environment Variables

Before running the project, ensure you have the following environment variables configured in a `.env` file at the root of your project. This file should not be shared publicly as it contains sensitive information.

#### Instructions

1. Create a `.env` file in the root directory of the project (if not already present).
2. Copy the environment variables listed in .env.example into your `.env` file.


> **Warning:** ⚠️ You need the MongoDB key to access real-time IoT data. As the data used in this demo was scraped from Google Maps, we can't publicly release it. Please reach out to us.




Run the following command to export environment variables from a `.env` file into your system environment.

```bash
bash export_env.sh
source ~/.bashrc
```

### 7. create services descriptions vectorDB

1. Navigate to the vector_db folder:

```bash
cd src/vector_db/
```

2. Create services descriptions vector database:

```bash
python create_vectordb.py
```

### 8. Run the Demo

Start the demo run the following demo in `src`:

```bash
uvicorn main:app --reload
```

### 7. Access the Application

1. Follow the instructions provided in the terminal output to access the application, usually via `http://127.0.0.1:8000/docs`.
2. To try the IoT- Agentic Search Engine (IoT-ASE), click the try button on the query API and replace `"string"` in the `text` value with your query and put a random `threadid` value, for instance

```json
{
  "text": "I want to get coffee",
  "threadId": "1234"
}
```

3. Click on the execute button and wait until you receive the response.

## Configuration

The devcontainer is configured using the following files:

- **`.devcontainer/devcontainer.json`**: Defines the container settings.
- **`Dockerfile`**: Customizes the development container image.
- **`setup-demo.sh`**: Installs dependencies required for the demo.

Feel free to adjust these files to fit your needs.

## Troubleshooting

- Ensure Docker is running on your system.
- If the container build fails, clear the cache and try again:

  ```bash
  Dev Containers: Rebuild Container
  ```

  (accessible via `Ctrl+Shift+P` or `F1`).

- Check for common issues in the [Dev Containers documentation](https://code.visualstudio.com/docs/devcontainers/containers).

## Contributing

Feel free to open issues or submit pull requests if you find any bugs or have suggestions for improvement.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Citation

We now have a paper you can cite for 🤗 the IoT Agentic Search Engine

```bibtex
@misc{elewah2025agenticsearchenginerealtime,
      title={Agentic Search Engine for Real-Time IoT Data}, 
      author={Abdelrahman Elewah and Khalid Elgazzar},
      year={2025},
      eprint={2503.12255},
      archivePrefix={arXiv},
      primaryClass={cs.NI},
      url={https://arxiv.org/abs/2503.12255}, 
}
```