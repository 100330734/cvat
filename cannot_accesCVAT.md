# Install CVAT Annotation Tool

# Author: Daniel Barrejón Moreno

# Install CVAT with GPU support

If the tool cannot be accessed, then :


## 1. Stop CVAT containers

```
docker-compose down
```


## 2.  RUN DOCKER IMAGES: RUN CVAT

```
sudo docker-compose -f  docker-compose.yml -f components/cuda/docker-compose.cuda.yml -f components/analytics/docker-compose.analytics.yml -f components/openvino/docker-compose.openvino.yml -f components/tf_annotation/docker-compose.tf_annotation.yml up -d
```
