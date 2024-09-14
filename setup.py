import os
import subprocess
import sys


def run_command(command):
    subprocess.run(command, shell=True, check=True)


def main():
    venv_name = "venv"

    # Create virtual environment
    run_command(f"{sys.executable} -m venv {venv_name}")

    # Determine the activate script path
    if sys.platform == "win32":
        activate_script = f"{venv_name}\\Scripts\\activate"
    else:
        activate_script = f"source {venv_name}/bin/activate"

    # Create or update requirements.in
    with open("requirements.in", "w") as f:
        f.write("requests\npython-dotenv\n")

    # Install pip-tools
    run_command(f"{activate_script} && pip install pip-tools")

    # Compile requirements.in to requirements.txt
    run_command(f"{activate_script} && pip-compile requirements.in")

    # Install packages from requirements.txt
    run_command(f"{activate_script} && pip install -r requirements.txt")

    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("# Add your environment variables here\n")

    # Create .env.example file
    with open(".env.example", "w") as f:
        f.write("# Example environment variables\n")
        f.write("API_KEY=your_api_key_here\n")
        f.write("DEBUG=False\n")

    # Create .gitignore if it doesn't exist, or append to it
    gitignore_content = f"{venv_name}/\n.env\n"
    if not os.path.exists(".gitignore"):
        with open(".gitignore", "w") as f:
            f.write(gitignore_content)
    else:
        with open(".gitignore", "a") as f:
            f.write(f"\n{gitignore_content}")

    print(
        "Setup complete. Virtual environment created, packages installed, and necessary files generated."
    )


if __name__ == "__main__":
    main()
