**Building the Python Application**

This guide details how to build your Python application using Docker. It assumes you have Docker installed and running on your system.

**Prerequisites**

  - Docker: [https://www.docker.com/get-started](https://www.google.com/url?sa=E&source=gmail&q=https://www.docker.com/get-started)

**Steps**

1.  **Clone or Download the Repository:**
    Obtain the project's source code by cloning the Git repository or downloading the archive.

2.  **Navigate to the Project Directory:**
    Use the `cd` command to enter the project directory:
    ```bash
    cd telegram_bot
    ```

3.  **Build the Docker Image:**
    Run the following command to build the Docker image:
    ```bash
    docker build -t telegram_bot .
    ```

4.  **Run the Application:**
    After building the image, you can run a container based on it:
    ```bash
    docker run -it telegram_bot
    ```

5.  **Execute Your Application:**
    Within the container, navigate to your application's working directory (`/app`) and run your main script:
    ```bash
    cd /app
    python main.py
    ```

**Additional Notes**

  - Consider creating a `.dockerignore` file to exclude unnecessary files from the image build process, optimizing image size.
  - For production use, you might explore building multi-stage images to reduce the final image size.
  - The `-it` flag in the `docker run` command is optional if you don't need an interactive shell within the container.