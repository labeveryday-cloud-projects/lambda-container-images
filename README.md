# lambda-container-images
This repo walks through how to use container images with Lambda

>NOTE: When using a container you will not see your code in console.

1. Create a new dir. Here we use example/hello-world 
2. Create your lambda function code. Here we use /example/lambda_function.py
3. Create a requirements.txt file that contains all of your dependencies
4. Create a Dockerfile that contains your image, code and runtime dependencies
5. Ensure docker desktop is running. The easy way is to open the Docker app. 

```bash
open --background -a /Applications/Docker.app

docker info
```

6. In the directory where you have your Dockerfile and artifacts, build the Docker image. *The following example uses the amd/64 platform, names the image docker-image, and gives it the test tag.*

```bash
docker build --platform linux/amd64 -t docker-image:test .
```

7. Verify the image: `docker image ls docker-image`
8. Run the Docker container to test the image locally: 

```bash
docker run --platform linux/amd64 -p 9000:8080 docker-image:test
```

9. Now that the container is running open a new terminal tab and invoke the function:

```bash
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```

Notice the response from the lambda function. 

10. Terminate the container with Ctrl+c
11. Verify its terminated with `docker ps`
12. Follow these steps to [create a new private repo in ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-create.html)

**(Optionally) You can follow these steps to do it from the CLI**

- Authenticate the Docker CLI to your Amazon ECR registry
    - Set the ``--region ``value to the AWS Region where you want to create the Amazon ECR repository.
    - Replace `111122223333` with your AWS account ID.

>NOTE: To get your account number you can open the AWS console or you can run: `aws sts get-caller-identity --query "Account" --output text`

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 111122223333.dkr.ecr.us-east-1.amazonaws.com
```

After running this you should see: *Login Succeeded*

- Now you will need to Create a repository in ECR:

```bash
aws ecr create-repository --repository-name hello-world --region us-east-1 --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
```

Here is a sample response:

```json
{
    "repository": {
        "repositoryArn": "arn:aws:ecr:us-east-1:111122223333:repository/hello-world",
        "registryId": "111122223333",
        "repositoryName": "hello-world",
        "repositoryUri": "111122223333.dkr.ecr.us-east-1.amazonaws.com/hello-world",
        "createdAt": 1711224470.414,
        "imageTagMutability": "MUTABLE",
        "imageScanningConfiguration": {
            "scanOnPush": true
        },
        "encryptionConfiguration": {
            "encryptionType": "AES256"
        }
    }
}
```

13. Once the repo is created be sure to copy the `repositoryUri`
14. Next we will tag the docker image. Be sure to replace `<ECRrepositoryUri>` with your own `repositoryUri`

```bash
docker tag docker-image:test <ECRrepositoryUri>:latest
```

15. Now you can push your image to ECR so it can be used by lambda:

```bash
docker push 111122223333.dkr.ecr.us-east-1.amazonaws.com/hello-world:latest
```

16. Create a lambda execution role named `lambda-ex` that lambda will assume:

```bash
aws iam create-role --role-name lambda-ex --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
```

You can also attach a policy from a document:

```bash
# Create the policy
aws iam create-policy --policy-name bedrock-lambda-policy --policy-document file://
policy.json

# Attach the Lambda Basic Execution policy to the role
aws iam attach-role-policy \
--role-name bedrock-lambda-role \
--policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Attach the bedrock-lambda-policy to the role
aws iam attach-role-policy \
--role-name bedrock-lambda-role \
--policy-arn arn:aws:iam::111122223333:policy/bedrock-lambda-policy
```

17. Copy the arn of the lambda: `arn:aws:iam::<Account Number>:role/lambda-ex`
18. Create a new lambda function using your image and IAM role:

```bash
aws lambda create-function \
  --function-name langchain-invoke \
  --package-type Image \
  --code ImageUri=111122223333.dkr.ecr.us-east-1.amazonaws.com/langchain:latest \
  --role arn:aws:iam::111122223333:role/bedrock-lambda-role
```

19. Test the lambda by invoking it:

```bash
aws lambda invoke --function-name langchain-invoke response.json
```

Notice the output:

```json
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST"
}
```


>NOTE: Ensure that you have create a repository in ECR. See, [Creating a private repository](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-create.html)


### Resources

[Deploy Python Lambda functions with container images](https://docs.aws.amazon.com/lambda/latest/dg/python-image.html)

[Using Lambda defined runtime variables](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html#configuration-envvars-runtime)
