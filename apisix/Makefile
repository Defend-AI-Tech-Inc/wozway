.PHONY:	docker publish

DOCKER_REGISTRY := "public.ecr.aws/u1j5h7e7"
DOCKER_REPO := "aigateway"
DOCKER_IMAGE := "wauzeway"
IMAGE_TAG := "0.01-2"

docker:
	docker build . -t wauzeway:dev

publish:
	docker tag aigatewayapisix:dev ${DOCKER_REGISTRY}/${DOCKER_REPO}:${DOCKER_IMAGE}.${IMAGE_TAG}
	docker push ${DOCKER_REGISTRY}/${DOCKER_REPO}:${DOCKER_IMAGE}.${IMAGE_TAG}
