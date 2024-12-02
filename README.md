
# IoT-Agentic-Search-Engine

This repository provides the IoT-Agentic-Search-Engine project that leverages a [DevContainer](https://code.visualstudio.com/docs/devcontainers/containers) for a seamless development environment setup. Follow the instructions below to install and start the demo.

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
git clone https://github.com/your-repo/demo-project.git
cd demo-project
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
3. Replace the empty values with the appropriate keys and URLs.

Run the following command to export environment variables from a `.env` file into your system environment. 

```bash
bash export_env.sh
```

### 7. create services descriptions vectorDB:
1. Navigate to the vector_db folder:
```bash
cd src/vector_db/
```
2. Create services descriptions vector database:
```bash
python create_vectordb.py
```

### 6. Run the Demo

Start the demo using:

```bash
./start-demo.sh
```

### 7. Access the Application

Follow the instructions provided in the terminal output to access the application, usually via `http://localhost:<port>`.

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

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
