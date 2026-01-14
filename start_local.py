#!/usr/bin/env python
"""
Simplified local-only startup script for wozway.
No DefendAI API registration required - just uses local config.
"""
import os
import subprocess
import yaml
import logging
import argparse
from jinja2 import Environment, FileSystemLoader
import sys
import webbrowser
import threading
import time
import re
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def check_docker_running():
    """Check if Docker Engine is running by executing 'docker info'."""
    try:
        subprocess.run(["docker", "info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logging.info("Docker Engine is running.")
        return True
    except subprocess.CalledProcessError:
        print("\n" + "="*60)
        print("❌ Docker Engine is not running")
        print("="*60)
        print("\nPlease start Docker Desktop and try again.")
        print("\nOptions:")
        print("1. Start Docker Desktop manually")
        print("2. Exit")
        
        choice = input("\nPress Enter after starting Docker, or type 'exit' to quit: ").strip().lower()
        if choice == 'exit':
            print("\nExiting. Goodbye!")
            sys.exit(0)
        
        # Try again after user confirms
        return check_docker_running()
    except FileNotFoundError:
        print("\n" + "="*60)
        print("❌ Docker is not installed")
        print("="*60)
        print("\nDocker is required to run wozway.")
        print("\nPlease install Docker Desktop from:")
        print("  https://www.docker.com/products/docker-desktop")
        print("\nAfter installation, run this script again.")
        sys.exit(1)

def prompt_for_llm_config():
    """Interactively prompt user for LLM provider and API key."""
    print("\n" + "="*60)
    print("LLM Provider Configuration")
    print("="*60)
    
    # Choose provider
    while True:
        print("\nWhich LLM provider would you like to use?")
        print("1. Groq")
        print("2. OpenAI (coming soon)")
        print("3. Exit")
        choice = input("Enter 1, 2, or 3: ").strip().lower()
        
        if choice == "1":
            llm_provider = "groq"
            print("\nYou selected: Groq")
            break
        elif choice == "2":
            print("\nOpenAI support coming soon! Please select Groq for now.")
            continue
        elif choice == "3" or choice == "exit":
            print("\nExiting setup. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    
    # Get API key
    while True:
        api_key = input(f"\nEnter your {llm_provider.upper()} API key (or 'exit' to quit): ").strip()
        
        if api_key.lower() == 'exit':
            print("\nExiting setup. Goodbye!")
            sys.exit(0)
        
        if not api_key:
            print("API key cannot be empty. Please try again.")
            continue
        
        # Validate format
        if llm_provider == "groq" and not api_key.startswith("gsk_"):
            print("Warning: Groq API keys typically start with 'gsk_'")
            confirm = input("Continue anyway? (y/n/exit): ").strip().lower()
            if confirm == 'exit':
                print("\nExiting setup. Goodbye!")
                sys.exit(0)
            if confirm != 'y':
                continue
        
        break
    
    return llm_provider, api_key

def save_config(llm_provider, llm_api_key, config_path="config.local.yaml"):
    """Save configuration to YAML file."""
    config = {
        "tenant": {
            "name": "local",
            "api_key": "local-api-key"
        },
        "llm_providers": {
            llm_provider: {
                "api_key": llm_api_key
            }
        }
    }
    
    with open(config_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
    
    logging.info(f"Configuration saved to {config_path}")

def load_config(config_path="config.yaml"):
    """Load configuration from a YAML file."""
    logging.info("Loading configuration from %s", config_path)

    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        logging.error("Configuration file %s not found", config_path)
        raise
    except yaml.YAMLError as e:
        logging.error("Error parsing YAML configuration file %s: %s", config_path, e)
        raise

    # Extract tenant configuration
    tenant_name = config.get("tenant", {}).get("name", "local")
    tenant_api_key = config.get("tenant", {}).get("api_key", "local-api-key")

    # Extract LLM provider configuration
    llm_providers = config.get("llm_providers", {})
    if llm_providers:
        llm_provider = next(iter(llm_providers.keys()), "groq")
        llm_api_key = llm_providers.get(llm_provider, {}).get("api_key", "")
    else:
        logging.error("No LLM providers found in configuration")
        sys.exit(1)

    if not llm_api_key:
        logging.error("LLM API key is required in config.yaml")
        sys.exit(1)

    config_data = {
        "tenant_name": tenant_name,
        "tenant_api_key": tenant_api_key,
        "llm_provider": llm_provider,
        "llm_api_key": llm_api_key
    }

    logging.info("Configuration loaded successfully")
    logging.info(f"Tenant: {tenant_name}")
    logging.info(f"LLM Provider: {llm_provider}")
    return config_data

def render_template(template_path, output_path, variables):
    """Render a Jinja2 template with provided variables."""
    logging.info("Rendering template %s to %s", template_path, output_path)

    env = Environment(loader=FileSystemLoader(searchpath='.'))
    template = env.get_template(template_path)
    content = template.render(variables)
    
    with open(output_path, 'w') as output_file:
        output_file.write(content)
    logging.info("Template rendering complete")

def spinner(stop_event):
    """Simple spinner to indicate progress."""
    spinner_chars = ['|', '/', '-', '\\']
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f'\rStarting services... {spinner_chars[idx % len(spinner_chars)]}')
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    sys.stdout.write('\rServices started!     \n')

def test_gateway_connection(max_retries=30, retry_delay=2):
    """Test if the gateway is responding correctly."""
    print("\n" + "="*60)
    print("Testing Gateway Connection")
    print("="*60)
    
    gateway_url = "http://localhost:9080/openai/v1/models"
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\nAttempt {attempt}/{max_retries}: Testing gateway at {gateway_url}")
            response = requests.get(gateway_url, timeout=5)
            
            if response.status_code == 200:
                print("✓ Gateway is responding correctly!")
                try:
                    models = response.json()
                    if 'data' in models:
                        print(f"✓ Found {len(models['data'])} available models")
                        print("\nAvailable models:")
                        for model in models['data'][:5]:  # Show first 5 models
                            print(f"  - {model.get('id', 'unknown')}")
                        if len(models['data']) > 5:
                            print(f"  ... and {len(models['data']) - 5} more")
                except:
                    print("✓ Gateway responded but couldn't parse models")
                return True
            elif response.status_code == 401:
                print("✗ Gateway returned 401 Unauthorized")
                print("  This likely means your API key is invalid or expired")
                return False
            else:
                print(f"✗ Gateway returned status code: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  Gateway not ready yet, waiting {retry_delay}s...")
        except requests.exceptions.Timeout:
            print(f"  Request timed out, waiting {retry_delay}s...")
        except Exception as e:
            print(f"  Error: {e}")
        
        if attempt < max_retries:
            time.sleep(retry_delay)
    
    print("\n✗ Gateway test failed after maximum retries")
    print("  The services are running but the gateway may not be configured correctly")
    return False

def run_docker_compose():
    """Run 'docker-compose up' with a spinner and open browser on specific log line."""
    try:
        logging.info("Starting docker-compose up")
        process = subprocess.Popen(
            ["docker", "compose", "up", "-d"],  # Run in detached mode
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Wait for process to complete
        for line in process.stdout:
            print(line, end='')

        process.wait()
        
        if process.returncode == 0:
            print("\n✓ Docker containers started successfully!")
            return True
        else:
            print(f"\n✗ Docker compose failed with return code {process.returncode}")
            return False

    except subprocess.CalledProcessError as e:
        logging.error("An error occurred while running docker-compose: %s", e)
        return False

def open_browser():
    """Open browser to OpenWebUI."""
    print("\n" + "="*60)
    print("Opening OpenWebUI in your browser...")
    print("="*60)
    print("\nURL: http://localhost:8084")
    print("\nIf the browser doesn't open automatically, please navigate to:")
    print("  http://localhost:8084")
    print("\nTo stop services, run: docker compose down")
    print("="*60 + "\n")
    
    time.sleep(2)  # Give services a moment to fully start
    webbrowser.open('http://localhost:8084')

def main():
    parser = argparse.ArgumentParser(description="Start wozway locally without DefendAI API registration")
    parser.add_argument("--config", help="Path to existing configuration YAML file (skips interactive setup)")
    parser.add_argument("--skip-test", action="store_true", help="Skip gateway connection test")
    args = parser.parse_args()

    print("=" * 60)
    print("Starting wozway in LOCAL-ONLY mode")
    print("No DefendAI API registration required")
    print("=" * 60)
    print("\n💡 Tip: Press Ctrl+C at any time to exit")
    print()

    # Check Docker is running
    check_docker_running()

    # Get or load configuration
    if args.config:
        # Load from existing config file
        try:
            config_vars = load_config(args.config)
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            sys.exit(1)
    else:
        # Interactive setup
        llm_provider, llm_api_key = prompt_for_llm_config()
        
        # Save configuration
        save_config(llm_provider, llm_api_key)
        
        config_vars = {
            "tenant_name": "local",
            "tenant_api_key": "local-api-key",
            "llm_provider": llm_provider,
            "llm_api_key": llm_api_key
        }

    # Render docker-compose.yml
    render_template("docker-compose.yml.j2", "docker-compose.yml", config_vars)

    # Start services
    print()
    print("Starting services with docker-compose...")
    print()
    
    if not run_docker_compose():
        sys.exit(1)
    
    # Test gateway connection
    if not args.skip_test:
        time.sleep(5)  # Give services time to initialize
        gateway_ok = test_gateway_connection()
        
        if not gateway_ok:
            print("\n⚠ Warning: Gateway test failed, but services are running")
            print("You may need to check your API key or wait a bit longer")
    
    # Open browser
    open_browser()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutdown requested. Exiting.")
        sys.exit(0)
