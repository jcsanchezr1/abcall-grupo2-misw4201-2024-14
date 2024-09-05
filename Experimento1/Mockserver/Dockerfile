# Dockerfile
FROM wiremock/wiremock:3.9.1-1
COPY stubs /home/wiremock
ENTRYPOINT ["/docker-entrypoint.sh", "--global-response-templating", "--disable-gzip", "--verbose"]