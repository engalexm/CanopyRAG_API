Whats up Alex

Whats up Will

Lambda Deployment steps (while logged into EC2)
1. Log into Docker via `docker login`. 
    - See "Push image to ECS" in "Links" section below for full `docker login` command and how to get password via AWS console.
    - Use `repositoryUri` in `ecs_repo_details.json` when doing the above.
2. Build image: `./docker_build.sh`
3. Tag image: `docker tag canopy-rag-api 905418383287.dkr.ecr.us-east-1.amazonaws.com/canopy-rag-api`
4. Push image: `docker push 905418383287.dkr.ecr.us-east-1.amazonaws.com/canopy-rag-api`
5. Go to Lambda in AWS Console --> Image --> Deploy new image --> Enter `905418383287.dkr.ecr.us-east-1.amazonaws.com/canopy-rag-api` and select `latest`-tagged image
6. Profit

Links:
- [Build Python Lambda image using AWS base image](https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-instructions)
- [Push image to ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-container-image.html)
