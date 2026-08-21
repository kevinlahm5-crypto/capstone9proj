#!/bin/bash
dnf install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<html><body><h1>Capstone9 Test App</h1><p>This is a sample web application for WAF testing.</p></body></html>" > /var/www/html/index.html
