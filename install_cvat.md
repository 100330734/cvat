# Install CVAT Annotation Tool

# Author: Daniel Barrejón Moreno

# Install CVAT with GPU support


## 1. Install NVIDIA Docker

Follow the following steps from this [link](https://github.com/NVIDIA/nvidia-docker/blob/master/README.md).

## 2. Install CVAT with GPU

Follow the steps on this [link](https://github.com/opencv/cvat/blob/develop/components/cuda/README.md).


## BUILD DOCKER IMAGES: COMPILE cvat

GPU, OpenVINO, TF Object Detection and Analytics management compilation

```sh
sudo docker-compose -f  docker-compose.yml -f components/cuda/docker-compose.cuda.yml -f components/analytics/docker-compose.analytics.yml -f components/openvino/docker-compose.openvino.yml -f components/tf_annotation/docker-compose.tf_annotation.yml build
```
## RUN DOCKER IMAGES: RUN cvat

```sh
sudo docker-compose -f  docker-compose.yml -f components/cuda/docker-compose.cuda.yml -f components/analytics/docker-compose.analytics.yml -f components/openvino/docker-compose.openvino.yml -f components/tf_annotation/docker-compose.tf_annotation.yml up -d
```

## STOP ALL CONTAINERS


```sh
sudo docker-compose down
```
