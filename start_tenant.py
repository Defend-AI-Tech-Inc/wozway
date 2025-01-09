#!/usr/bin/env python
import os
import subprocess
import yaml
import logging
import argparse
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import hashlib
import requests
import json
import sys
import webbrowser
import threading
import time
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Defaults
API_BASE_URL = 'https://playground.defendai.tech'
DEFAULT_TENANT_NAME="synergy"
DEFAULT_TENANT_API_KEY="f64a2d8a-d746-4d01-8059-82981016b6e6"
DEFAULT_LLM_PROVIDER="groq"
DEFAULT_LLM_API_KEY="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"
PLACEHOLDER_VALUES = {"your_tenant_name", "defendai_api_key", "groq_api_key"}

def check_docker_running():
    """Check if Docker Engine is running by executing 'docker info'."""
    try:
        subprocess.run(["docker", "info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logging.info("Docker Engine is running.")
    except subprocess.CalledProcessError:
        logging.error("Docker Engine is not running. Please start Docker and try again.")
        sys.exit(1)
    except FileNotFoundError:
        logging.error("Docker is not installed on this system. Please install Docker and try again.")
        sys.exit(1)

def load_config(config_path="config.yaml"):
    """Load configuration from a YAML file, substituting defaults for placeholder values."""
    logging.info("Loading configuration from %s", config_path)

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Load or substitute tenant configuration
    tenant_name = config.get("tenant", {}).get("name", DEFAULT_TENANT_NAME)
    if tenant_name in PLACEHOLDER_VALUES:
        logging.warning("Using default tenant name due to placeholder value")
        tenant_name = DEFAULT_TENANT_NAME

    tenant_api_key = config.get("tenant", {}).get("api_key", DEFAULT_TENANT_API_KEY)
    if tenant_api_key in PLACEHOLDER_VALUES:
        logging.warning("Using default tenant API key due to placeholder value")
        tenant_api_key = DEFAULT_TENANT_API_KEY

    # Load or substitute LLM provider configuration
    llm_providers = config.get("llm_providers", {})
    llm_provider = next(iter(llm_providers.keys()), DEFAULT_LLM_PROVIDER)
    llm_api_key = llm_providers.get(llm_provider, {}).get("api_key", DEFAULT_LLM_API_KEY)

    if llm_provider in PLACEHOLDER_VALUES:
        logging.warning("Using default LLM provider due to placeholder value")
        llm_provider = DEFAULT_LLM_PROVIDER
    if llm_api_key in PLACEHOLDER_VALUES:
        logging.warning("Using default LLM API key due to placeholder value")
        llm_api_key = DEFAULT_LLM_API_KEY

    config_data = {
        "tenant_name": tenant_name,
        "tenant_api_key": tenant_api_key,
        "llm_provider": llm_provider,
        "llm_api_key": llm_api_key
    }

    logging.info("Configuration loaded: %s", config_data)
    return config_data


def render_template(template_path, output_path, variables, dry_run=False):
    """Render a Jinja2 template with provided variables."""
    logging.info("Rendering template %s to %s", template_path, output_path)

    env = Environment(loader=FileSystemLoader(searchpath='.'))
    template = env.get_template(template_path)
    content = template.render(variables)
    
    if dry_run:
        print("\nGenerated docker-compose.yml content:\n")
        print(content)
    else:
        with open(output_path, 'w') as output_file:
            output_file.write(content)
        logging.info("Template rendering complete")


def run_docker_compose():
    """Run 'docker-compose up' with a spinner and open browser on specific log line."""
    try:
        logging.info("Starting docker-compose up")
        process = subprocess.Popen(
            ["docker", "compose", "up"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        stop_event = threading.Event()
        spinner_thread = threading.Thread(target=spinner, args=(stop_event,))
        spinner_thread.start()

        # Regex to detect "HTTP/1.1" 200
        target_pattern = re.compile(r'HTTP/1\.1"\s+200\b')
        browser_opened = False

        # Read the output line by line
        for line in process.stdout:
            if target_pattern.search(line) and not browser_opened:
                stop_event.set()
                spinner_thread.join()
                logging.info("DefendAI started successfully!\nNavigate to http://localhost:8084 if not done automatically.\nTo stop DefendAI, enter ctrl-c")
                webbrowser.open('http://localhost:8084')
                browser_opened = True

        # Wait for the subprocess to finish
        process.wait()

    except KeyboardInterrupt:
        logging.warning("Interrupted! Shutting down with 'docker-compose down -v'")
        subprocess.run(["docker", "compose", "down", "-v"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error("An error occurred while running docker-compose: %s", e)


# Function to generate a unique machine identifier (SHA-256 hash)
def generate_machine_uuid():
    try:
        machine_info = os.uname()  # Get system info
    except AttributeError:
        # For Windows 
        machine_info = {
            'sysname': os.name,
            'nodename': os.uname().nodename if hasattr(os, 'uname') else 'nodename',
            'release': 'release',
            'version': 'version',
            'machine': 'machine'
        }
        unique_string = (machine_info['sysname'] + machine_info['nodename'] +
                         machine_info['release'] + machine_info['version'] +
                         machine_info['machine'])
    else:
        unique_string = (machine_info.sysname + machine_info.nodename +
                         machine_info.release + machine_info.version +
                         machine_info.machine)
    
    sha_uuid = hashlib.sha256(unique_string.encode()).hexdigest()
    # Ensure UUID format
    formatted_uuid = f"{sha_uuid[:8]}-{sha_uuid[8:12]}-{sha_uuid[12:16]}-{sha_uuid[16:20]}-{sha_uuid[20:32]}"
    return formatted_uuid


# Function to generate license key
def generate_license_key(machine_uuid):
    """Generate a license key using the machine UUID."""
    url = f"{API_BASE_URL}/generate-license-key"
    headers = {"Content-Type": "application/json"}
    data = {"uuid": machine_uuid}  # Send the formatted UUID

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        response_data = response.json()

        license_key = response_data.get("licenseKey")
        status = response_data.get("status")

        if license_key:
            if status:  # If status is True, the license key is valid
                logging.info("License key generated successfully and is valid.")
                return license_key
            else:  # If status is False, the license key is invalid
                logging.error("The license key is invalid for registration.")
                print("A license key for this user already exists but is inactive. Please contact support at info@defendai.tech.")
                sys.exit(1)
        else:
            logging.error("License key not found in the response.")
            return None
    except requests.RequestException as e:
        logging.error("Error calling generate-license-key API: %s", e)
        return None


# Function to check if an email is registered
def check_registered_email(license_key, email_address):
    """Check if the user’s email can be used for registration."""
    url = f"{API_BASE_URL}/check-registered-email"
    headers = {
        'Content-Type': 'application/json',
        'auth-key': license_key  # Pass the license key as auth-key
    }
    data = {'email': email_address}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            registered = response.json().get('registered')
            return registered
        else:
            print(f"Failed to check registered email. Status: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error calling check-registered-email API: {e}")
        return None


# Function to save registration
def save_registration(license_key, fullname, email):
    """
    Save registration (no longer takes metadata).
    The backend will automatically assign a default Groq key to the tenant.
    """
    url = f"{API_BASE_URL}/save-registration"
    headers = {
        'Content-Type': 'application/json',
        'auth-key': license_key  # Pass the license key as auth-key
    }
    data = {
        'fullname': fullname,
        'email': email
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            vguid = response_data.get('vguid')
            if vguid:
                print("Registration successful")
                print(f"A verification OTP is sent to your email {email}")
                return vguid
            else:
                print("Registration failed: vguid not found in the response.")
                return None
        else:
            print(f"Registration failed. Status: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error calling save-registration API: {e}")
        return None

def verify_otp(vguid, otp):
    """
    Verify the OTP. 
    The response now includes tenant_id, api_key, llm_key, and llm_provider, 
    which will be used automatically in the docker-compose environment.
    """
    url = f"{API_BASE_URL}/verify_otp"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {'vguid': vguid, 'otp': otp}

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            tenant_id = response_data.get('tenant_id')
            api_key = response_data.get('api_key')
            llm_key = response_data.get('llm_key')
            llm_provider = response_data.get('llm_provider')
            if tenant_id and api_key and llm_key and llm_provider:
                return tenant_id, api_key, llm_key, llm_provider
            else:
                print("Failed to retrieve tenant_id, api_key, llm_key, or llm_provider from verify_otp response.")
                return None, None, None, None
        else:
            print(f"OTP verification failed. Status: {response.status_code}, Response: {response.text}")
            return None, None, None, None
    except Exception as e:
        print(f"Error calling verify_otp API: {e}")
        return None, None, None, None

# Function to resend OTP
def resend_otp(vguid):
    url = f"{API_BASE_URL}/resend_otp"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {'vguid': vguid, 'mode': 'script'}

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("OTP resent successfully.")
        else:
            print(f"Failed to resend OTP. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error calling resend_otp API: {e}")

def prompt_exit(option):
    if option.lower() == 'exit':
        print("Thank you for trying DefendAI!")
        sys.exit(0)

def spinner(stop_event):
    """Simple spinner to indicate progress."""
    spinner_chars = ['|', '/', '-', '\\']
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f'\rStarting DefendAI... {spinner_chars[idx % len(spinner_chars)]}')
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    sys.stdout.write('\rDefendAI build complete!     \n')

def exec_wauzeway(config_vars):
    """Use config_vars to render docker-compose.yml and then run docker-compose up."""
    logging.info("Rendering docker-compose and running Docker with:")
    logging.info(config_vars)

    # Render the template and create docker-compose.yml
    render_template("docker-compose.yml.j2", "docker-compose.yml", config_vars)

    # Run docker-compose up if not in dry-run mode
    run_docker_compose()


def proceed_with_registration():
    print("===Welcome to DefendAI Registration===\n")

    # Step 1: Generate Machine UUID
    machine_uuid = generate_machine_uuid()

    # Step 2: Generate License Key
    license_key = generate_license_key(machine_uuid)
    if not license_key:
        print("A License key for this user already exists, please contact support at info@defendai.tech.")
        sys.exit(1)

    while True:
        # Collect user information
        print("--- New Registration ---")

        # Step 3: Prompt for Email Address
        while True:
            email_address = input("Enter your email address (or type 'exit' to quit): ").strip()
            prompt_exit(email_address)

            if not email_address:
                print("Email address is required. Please try again.")
                continue

            # Check if the email is available for registration
            registered = check_registered_email(license_key, email_address)
            if registered is None:
                print("Unable to verify email registration status. Please try again later.")
                continue
            elif registered:
                print(f"Email '{email_address}' is available for registration.")
                break
            else:
                print(f"Email '{email_address}' is already registered. Please enter a different email or contact support at info@defendai.tech.")
                continue

        # Step 4: Prompt for Full Name
        while True:
            fullname = input("Enter your full name (or type 'exit' to quit): ").strip()
            prompt_exit(fullname)

            if not fullname:
                print("Full name is required. Please try again.")
                continue
            else:
                break

        # Display all collected information
        print("\nPlease review your information:")
        print(f"Email address: {email_address}")
        print(f"Full name: {fullname}")

        # Ask user to proceed or edit information
        while True:
            print("\nPlease select an option:")
            print("1. Proceed")
            print("2. Edit information")
            proceed_choice = input("Enter 1 or 2 (or 'exit' to quit): ").strip()
            prompt_exit(proceed_choice)

            if proceed_choice == '1':
                # Proceed with registration
                break
            elif proceed_choice == '2':
                # Allow user to edit
                while True:
                    print("\nWhich information would you like to edit?")
                    print("1. Email address")
                    print("2. Full name")
                    edit_choice = input("Enter 1 or 2 (or 'exit' to quit): ").strip()
                    prompt_exit(edit_choice)

                    if edit_choice == '1':
                        while True:
                            email_address = input("Enter your email address (or type 'exit' to quit): ").strip()
                            prompt_exit(email_address)

                            if not email_address:
                                print("Email address is required. Please try again.")
                                continue

                            # Check if the email is available for registration
                            registered = check_registered_email(license_key, email_address)
                            if registered is None:
                                print("Unable to verify email registration status. Please try again later.")
                                continue
                            elif registered:
                                print(f"Email '{email_address}' is available for registration.")
                                break
                            else:
                                print(f"Email '{email_address}' is already registered. Please enter a different email or contact support.")
                                continue
                        break
                    elif edit_choice == '2':
                        while True:
                            fullname = input("Enter your full name (or type 'exit' to quit): ").strip()
                            prompt_exit(fullname)

                            if not fullname:
                                print("Full name is required. Please try again.")
                                continue
                            else:
                                break
                        break
                    else:
                        print("Invalid input. Please enter '1' or '2'.")
                        continue
                # After editing, show info again, allow user to proceed or edit more
                continue
            else:
                print("Invalid input. Please enter '1' or '2'.")
                continue

        # If we reach here, user chose to proceed
        # Step 5: Save registration (API no longer takes metadata)
        vguid = save_registration(license_key, fullname, email_address)
        if not vguid:
            print("Registration failed. Please try again.")
            continue  # Go back to start

        # Step 6: Verify OTP
        otp_verified = False
        tenant_name = None
        tenant_api_key = None
        llm_key = None
        llm_provider = None

        while not otp_verified:
            print("\nOTP expires in 1 hour.")
            otp_input = input("Please enter the one-time password sent to your email or enter '1' to resend OTP (or 'exit' to quit): ").strip()
            prompt_exit(otp_input)

            if otp_input == '1':
                resend_otp(vguid)
            else:
                # Try to verify OTP
                tenant_id, api_key, assigned_llm_key, assigned_llm_provider = verify_otp(vguid, otp_input)
                if tenant_id and api_key and assigned_llm_key and assigned_llm_provider:
                    print("Success, your account is now verified. Enjoy using DefendAI.")
                    # set tenant_name, tenant_api_key, llm_provider, llm_api_key
                    tenant_name = tenant_id
                    tenant_api_key = api_key
                    llm_provider = assigned_llm_provider
                    llm_key = assigned_llm_key
                    otp_verified = True
                else:
                    print("Invalid OTP. Please try again.")

        if otp_verified:
            break

    # Build config_vars for docker compose
    config_vars = {
        "tenant_name": tenant_name,
        "tenant_api_key": tenant_api_key,
        "llm_provider": llm_provider,
        "llm_api_key": llm_key
    }

    # Save these config variables in 'config_saved.yaml'
    saved_config = {
        "tenant": {
            "name": tenant_name,
            "api_key": tenant_api_key
        },
        "llm_providers": {
            llm_provider: {
                "api_key": llm_key
            }
        }
    }
    with open("config_saved.yaml", "w") as file:
        yaml.dump(saved_config, file)

    return config_vars


def main(args):
    check_docker_running()
    if args.dry_run:
        config_vars = {
            "tenant_name": DEFAULT_TENANT_NAME,
            "tenant_api_key": DEFAULT_TENANT_API_KEY,
            "llm_provider": DEFAULT_LLM_PROVIDER,
            "llm_api_key": DEFAULT_LLM_API_KEY
        }
        print("Generating default config during dry run")
        render_template("docker-compose.yml.j2", "docker-compose.yml", config_vars, dry_run=args.dry_run)
        sys.exit(0)
    elif args.config:
        config_vars = load_config(args.config)
        print("Executing wauzeway proxy in docker-compose with config YAML")
        exec_wauzeway(config_vars)
        sys.exit(0)
    else:
        print("Welcome to DefendAI\n")
        while True:
            choice = input("Please select an option:\n1. Register a new user\n2. Use existing configuration to run the docker compose\nEnter 1 or 2 (or 'exit' to quit): ").strip()
            if choice == '1':
                config_vars = proceed_with_registration()
                exec_wauzeway(config_vars)
                break
            elif choice == '2':
                # Try to load existing configuration
                try:
                    config_vars = load_config("config_saved.yaml")
                    print("Executing wauzeway proxy in docker-compose with saved configuration")
                    exec_wauzeway(config_vars)
                except FileNotFoundError:
                    print("No saved configuration found. Please register a new user first.")
                    continue  # Go back to the choice
                break
            elif choice.lower() == 'exit':
                print("Thank you for using DefendAI!")
                sys.exit(0)
            else:
                print("Invalid input. Please enter '1' or '2'.")

if __name__ == "__main__":
    # Argument parser for --config and --dry-run options
    parser = argparse.ArgumentParser(
        description="Onboard to DefendAI and run wauzeway docker compose with optional dry-run or config file."
    )
    parser.add_argument(
        "--config", 
        required=False, 
        help="Path to the configuration YAML file to run from saved config without new registration."
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Only display the generated docker-compose.yml without running it"
    )
    args = parser.parse_args()

    try:
        main(args)
    except KeyboardInterrupt:
        print("\nRegistration script interrupted. Exiting.")
        sys.exit(0)
