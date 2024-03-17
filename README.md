# MLDev

prequites:

- Install Docker
- Install AWS Command Line

Run Docker

Run to enter configure mode

`aws configure`

AWS Access Key ID [AKIA4NH3CMESZ7QC2TWN]:
AWS Secret Access Key [MFuM/7SmD3ooouHjOYxAiqH63SBmZCd8ka6TfaFi]:
Default region name [us-east-2]:

Run to configure your terminal to allow pushing

`aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 853077549349.dkr.ecr.us-east-2.amazonaws.com/cookiq`

Then

`cd lambda`

Run the following to build an image called “recommendation-image” based on arm64 architecture, the : mean that we specific the latest image that has been made (in the case where you re-make this multiple times it would replace the latest image each time)

`docker build --platform=linux/arm64 -t recommendation-image:latest-[NAME] .`

Run the following to link the image to the AWS repository

`docker image tag recommendation-image:latest-[NAME] 853077549349.dkr.ecr.us-east-2.amazonaws.com/cookiq:latest`

Run the following to push the image to ECR

`docker push 853077549349.dkr.ecr.us-east-2.amazonaws.com/cookiq:latest-[NAME]`
