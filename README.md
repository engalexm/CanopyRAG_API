Whats up Alex

Whats up Will

1. Set up custom domain name with Route 53 OR freenom.com
2. Set up Load Balancer for EC2 instance
    - Target group: route to port 8888
    - Cert: Register new cert with ACM OR certbot/Let's Encrypt using custom domain
3. Profit

Lambda Deployment steps (while logged into EC2)
1. Log into Docker via `docker login`. 
    - See "Push image to ECS" in "Links" section below for full `docker login` command and how to get password via AWS console.
    - Use `repositoryUri` in `ecs_repo_details.json` when doing the above.
2. Build image: `./docker_build.sh`
3. Tag image: `docker tag canopy-rag-api 905418383287.dkr.ecr.us-east-1.amazonaws.com/canopy-rag-api`
4. Push image: `docker push 905418383287.dkr.ecr.us-east-1.amazonaws.com/canopy-rag-api`

Links:
- [Build Python Lambda image using AWS base image](https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-instructions)
- [Push image to ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-container-image.html)
