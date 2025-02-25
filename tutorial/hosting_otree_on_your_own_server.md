# Hosting oTree on Your Own Server

BEWARE : This tutorial hasn't been properly tested so it might not work well. We will update it as we go depending on time and user feedback. If you follow this tutorial and find anything that can be corrected please let us know.

## Introduction
This tutorial will guide you through the steps to host your oTree and DuckSoup application on your own server. Here we use a self-hosted solution, so you can have more control over your environment, the data you collect, and reduce costs associated with cloud services. We will also cover how to set up Nginx as a reverse proxy to manage traffic to your oTree application (don't worry, we will explain what this is and how it works).

## General Goal
The goal of this tutorial is to host your oTree and DuckSoup application on your own server. This will allow you to have full control over your hosting environment and run experiments and collect data directly on your machine.

## What is Nginx?
Nginx is a high-performance web server that can also be used as a reverse proxy, load balancer, and HTTP cache. It is known for its stability, rich feature set, simple configuration, and low resource consumption. In this tutorial, we will use Nginx to route incoming traffic to your oTree application running in a Docker container. More simply, Nginx will take the incoming requests from users and send them to the oTree application, it enables us to route the traffic to the oTree application and to manage it.

## Prerequisites
- A server with a Linux-based operating system (Ubuntu is recommended).
- If you want to collect a lot of participants in paralell (more than 24), consider using a server with 12+ cores, a very good internet connection and a graphics card (for intensive video effects). The graphics card we use in the lab is a Nvidia RTX A5000, because it can handle the encoding/decoding of more than 3 streams in parallel. 
- Basic knowledge of command line operations.

## Step 1: Setting Up Your Server

1. **Update Your Server**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Docker**:
   Follow the official Docker installation guide for your Linux distribution. For Ubuntu, you can use:
   ```bash
   sudo apt install docker.io
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

3. **Install Nginx**:
   ```bash
   sudo apt install nginx
   ```

## Step 2: Running oTree with Docker

1. **Create a Docker Network**:
   This will allow your oTree container to communicate with Nginx.
   ```bash
   docker network create otree_network
   ```

2. **Run the oTree Container**:

First, you need to build the oTree Docker image. This is done by running the following command inside the oTree directory.
   ```bash
   docker build -t your_otree_image .
   ```
Then, you can run the oTree container by running the following command:

   Replace `your_otree_image` with the name of your oTree Docker image.
   ```bash
   docker run --name otree_app --network otree_network -p 8000:8000 -d your_otree_image
   ```

## Step 3: Configuring Nginx

1. **Create a New Nginx Configuration File**:
   ```bash
   sudo nano /etc/nginx/sites-available/otree
   ```

2. **Add the Following Configuration**:
   Get your own IP adress by running the following command:
   ```bash
   ip addr show
   ```
   
   Then, replace `your_domain_or_ip` with your server's domain name or IP address.
   ```nginx
   server {
       listen 80;
       server_name your_domain_or_ip;

       location / {
           proxy_pass http://otree_app:8000;  # This points to the oTree container
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Enable the Configuration**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/otree /etc/nginx/sites-enabled/
   ```

4. **Test the Nginx Configuration**:
   ```bash
   sudo nginx -t
   ```

5. **Restart Nginx**:
   ```bash
   sudo systemctl restart nginx
   ```

## Step 3.1: Setting Up HTTPS with Let's Encrypt

## Why Use HTTPS?

Using HTTPS is essential for several reasons, especially when hosting applications that involve real-time communication, such as DuckSoup, which utilizes WebRTC technology. This is becayse WebRTC (Web Real-Time Communication) requires a secure context (HTTPS) to function properly in most modern browsers. This means that if you want to use features like video conferencing or real-time data sharing, your application must be served over HTTPS.

1. **Install Certbot**:
   Certbot is a tool to obtain and manage SSL certificates from Let's Encrypt.
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Obtain an SSL Certificate**:
   Run the following command to obtain an SSL certificate. Replace `your_domain_or_ip` with your server's domain name or IP address.
   ```bash
   sudo certbot --nginx -d your_domain_or_ip
   ```

   Follow the prompts to complete the certificate installation.

3. **Automatic Renewal**:
   Certbot sets up a cron job to automatically renew your certificates. You can test the renewal process with:
   ```bash
   sudo certbot renew --dry-run
   ```

4. **Update Nginx Configuration**:
   After obtaining the SSL certificate, Certbot will automatically update your Nginx configuration. However, you can manually check that your configuration includes the following:
   ```nginx
   server {
       listen 80;
       server_name your_domain_or_ip;
       return 301 https://$host$request_uri;  # Redirect HTTP to HTTPS
   }

   server {
       listen 443 ssl;
       server_name your_domain_or_ip;

       ssl_certificate /etc/letsencrypt/live/your_domain_or_ip/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your_domain_or_ip/privkey.pem;

       location / {
           proxy_pass http://otree_app:8000;  # This points to the oTree container
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

5. **Restart Nginx**:
   After making changes, restart Nginx to apply the new configuration.
   ```bash
   sudo systemctl restart nginx
   ```

## Step 4: Accessing Your oTree Application

- You can now access your oTree application by navigating to `http://your_domain_or_ip` in your web browser.

## Conclusion
You have successfully set up your oTree application on your own server using Docker and Nginx. This setup allows you to have full control over your hosting environment and can be customized further based on your needs. For more advanced configurations, consider exploring SSL setup for secure connections and load balancing options. 