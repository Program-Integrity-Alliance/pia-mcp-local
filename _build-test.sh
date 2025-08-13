docker build -t pia-mcp-server:latest .
export IMAGE=docker.io/astrobagel/pia-mcp:0.1.0
docker build -t $IMAGE .
docker push $IMAGE
