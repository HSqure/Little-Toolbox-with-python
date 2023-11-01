# Vitis-AI 3.5 基础教程

# 1. 安装


## 1.1 依赖配置

### 1.1.1 Docker安装与配置
#### 🟦 Step 1:
首先检测是否有旧版本，如果有，将其清理干净，输入以下命令进行卸载：
```shell
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
``` 
> ⚠️注意：  运行后`apt-get`或许会提示未安装过组件。
### 🟦 Step 2:
添加`docker`官方的`GPG密钥`:
```shell
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```
#### 🟦 Step 3:
添加`docker`软件源仓库并更新：
```shell
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
#### 🟦 Step 4:
配置好之后就可以安装`docker`了：
```shell
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
> ⚠️注意：刚安装好时，根据docker默认配置，不得不使用高权限`sudo`来运行，随后将当前用户`$USER`添加进用户组后，将不再需要使用`sudo`来运行，使用普通用户身份即可。

让我们运行以下命令来验证一下刚装好的`docker`吧：
```shell
sudo docker run hello-world
```

>✅ 如果看到如下信息，则表示安装成功:
>```shell
>Unable to find image 'hello-world:latest' locally
>latest: Pulling from library/hello-world
>719385e32844: Pull complete 
>Digest: >sha256:88ec0acaa3ec199d3b7eaf73588f4518c25f9d34f58ce9a0df68429c5af>48e8d
>Status: Downloaded newer image for hello-world:latest
>
>Hello from Docker!
>This message shows that your installation appears to be working >correctly.
>
>To generate this message, Docker took the following steps:
> 1. The Docker client contacted the Docker daemon.
> 2. The Docker daemon pulled the "hello-world" image from the >Docker Hub.
>    (amd64)
> 3. The Docker daemon created a new container from that image >which runs the
>    executable that produces the output you are currently reading.
> 4. The Docker daemon streamed that output to the Docker client, >which sent it
>    to your terminal.
>
>To try something more ambitious, you can run an Ubuntu container >with:
> $ docker run -it ubuntu bash
>
>Share images, automate workflows, and more with a free Docker ID:
> https://hub.docker.com/
>
>For more examples and ideas, visit:
> https://docs.docker.com/get-started/
>
>```

#### 🟦 Step 5:
创建`docker`用户组：
```shell
sudo groupadd docker
```
将你的当前用户添加进用户组：
```shell
sudo usermod -aG docker $USER
```
登出当前系统并且重新登录后，应用刚刚的设置。
```shell
newgrp docker
```
再试试以普通用户身份运行前面步骤中的`hello-world`测试。
```shell
docker run hello-world
```
和之前打印显示一致的话，就代表已经设置成功了！你的当前用户以及被添加进`docker`的用户组，以后`docker`操作无需再使用`sudo`。至此，docker基本安装以及设置已经完成！

#### 🟦 附录：网络环境配置
> 💡  小Tips:
> 如果有使用proxy需求，注意需要手动配置`docker`的`proxy`，将下方指令中的`你的proxy地址`和`你的proxy端口`修改成你自己的地址以及端口后执行：
> ```shell
> mkdir -p /etc/systemd/system/docker.service.d
> echo '[Service]' >> ~/etc/systemd/system/docker.service.d/http-proxy.conf
> echo 'Environment="HTTP_PROXY=http://你的proxy地址:你的proxy端口/"' >> ~/etc/systemd/system/docker.service.d/http-proxy.conf
> systemctl daemon-reload
> service docker restart
>```


### 1.1.2 NVIDIA Docker组件安装与配置
NVIDIA Docker的组件即`NVIDIA Container Toolkit packages`，为在`docker`中调度GPU提供了支持。
#### 🟩 Step 1:
输入以下命令配置官方的`GPG密钥`，并且添加系统的软件源仓库：
```shell
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list \
  && \
    sudo apt-get update
```
#### 🟩 Step 2:
仓库配置好之后就可以安装`NVIDIA Container Toolkit packages`组件了：
```shell
sudo apt-get install -y nvidia-container-toolkit
```
#### 🟩 Step 3:
安装好组件后对`docker`进行配置：
```shell
sudo nvidia-ctk runtime configure --runtime=docker
```
惯例重启`docker`服务：
```shell
sudo systemctl restart docker
```
#### 🟩 Step 4:
对`NVIDIA docker`进行运行测试：
```shell
docker run --gpus all nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04 nvidia-smi
```
运行会下载NVIDIA的docker进行测试，我们可以查看运行后的打印信息来检查是否配置成功：
>✅ 如果看到如下类似`nvidia-smi`正常运行的信息，则表示配置成功:
>```shell
> Unable to find image 'nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04' locally
> 11.3.1-cudnn8-runtime-ubuntu20.04: Pulling from nvidia/cuda
> 56e0351b9876: Already exists 
> 18e5fdd4cb87: Pull complete 
> 645133b03941: Pull complete 
> b4a1420ffd93: Pull complete 
> 7e1f4dad10e9: Pull complete 
> 552678304786: Pull complete 
> da8df3f1d840: Pull complete 
> 46a89842b228: Pull complete 
> 2effcdc05756: Pull complete 
> e3cafc127f62: Pull complete 
> Digest: sha256:8eac179cf661ff33a55200d8d60b62d987ff4ad8c1d1b1be4c4378ef0f859716
> Status: Downloaded newer image for nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04
> 
> ==========
> == CUDA ==
> ==========
> 
> CUDA Version 11.3.1
> 
> Container image Copyright (c) 2016-2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
> 
> This container image and its contents are governed by the NVIDIA Deep Learning Container License.
> By pulling and using the container, you accept the terms and conditions of this license:
> https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license
> 
> A copy of this license is made available in this container at /NGC-DL-CONTAINER-LICENSE for your convenience.
> 
> Mon Oct 30 06:53:42 2023       
> +---------------------------------------------------------------------------------------+
> | NVIDIA-SMI 535.98                 Driver Version: 535.98       CUDA Version: 12.2     |
> |-----------------------------------------+----------------------+----------------------+
> | GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
> | Fan  Temp   Perf          Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M. |
> |                                         |                      |               MIG M. |
> |=========================================+======================+======================|
> |   0  NVIDIA GeForce GTX 1080 Ti     Off | 00000000:09:00.0  On |                  N/A |
> |  0%   55C    P0              68W / 250W |    863MiB / 11264MiB |      6%      Default |
> |                                         |                      |                  N/A |
> +-----------------------------------------+----------------------+----------------------+
>                                                                                          
> +---------------------------------------------------------------------------------------+
> | Processes:                                                                            |
> |  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
> |        ID   ID                                                             Usage      |
> |=======================================================================================|
> +---------------------------------------------------------------------------------------+
> 
> 
>```

## 1.2 Vitis-AI Docker镜像安装

在一切开始之前，首先指定你的`Vitis-AI`的路径：
```shell
export VITIS_AI_HOME=你的Vitis-AI路径
```

### 1.2.1 网络环境配置（可选）
> ⚠️注意: 如果能正常使用`proxy`资源，则可跳过[网络环境配置](#121-网络环境配置可选)阶段（1.2.1）。

由于docker使用默认系统配置的是`deb http://us.archive.ubuntu.com/ubuntu/ focal universe`软件源，服务器难以保证`docker`在编译安装时的速度。此时，在没有`proxy`资源帮助解决问题的情况下，可以尝试修改软件源来加快编译安装的速度。需要完成修改**以下两处**配置文件：
#### 🟥 文件1：Vitis-AI的docker软件源配置文件
在`$VITIS_AI_HOME/docker/common/install_base.sh`中，将文件的`第28行`到`第32行`：
```shell
chmod 1777 /tmp \
    && mkdir /scratch \
    && chmod 1777 /scratch \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
```
修改成：
```shell
RUN sed --in-place --regexp-extended "s/(\/\/)(archive\.ubuntu)/\1cn.\2/" /etc/apt/sources.list && apt-get update && apt-get install -y --no-install-recommends \
```

#### 🟥 文件2：系统的软件源配置文件
首先将文件`/etc/apt/sources.list`进行备份：
```shell
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak 
```
然后我们就可以打开文件进行修改了：
```shell
sudo gedit /etc/apt/sources.list
```
这里需要将其中内容全部清空并替换为如下源，这里推荐使用阿里的源：
```shell
deb http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse
# deb http://mirrors.aliyun.com/ubuntu/ focal-proposed main restricted universe multiverse
# deb-src http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
# deb-src http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
# deb-src http://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse
# deb-src http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
# deb-src http://mirrors.aliyun.com/ubuntu/ focal-proposed main restricted universe multiverse
```
> 💡 小Tips:
> 除此之外，还有更多源可在[此处](https://momane.com/change-ubuntu-20-04-source-to-china-mirror)选择。



### 1.2.2 Vitis-AI Docker安装
在本地安装Vitis-AI docker**有两个分支选项**，预编译的版本仅支持CPU，GPU版本只能本地编译。出于速度以及质量考虑，如果设备满足要求则推荐使用GPU版本。

#### 🟥 选项 1：使用预编译 Vitis-AI Docker

| 软件框架     | 硬件架构 | docker所包含工具              |
| :---------- | :----- | :-----------------------      |
| pytorch     | cpu    | `PyTorch（仅CPU版本）`          | 
| tensorflow2 | cpu    | `TensorFlow 2 （仅CPU版本）`    |
| tensorflow  | cpu    | `TensorFlow 1.15 （仅CPU版本）` |
| pytorch     | rocm   | `PyTorch`  `ROCm`             |
| tensorflow2 | rocm   | `TensorFlow 2`  `ROCm`        |


根据上方表格选择参数，选择自己所需的docker image从docker服务器下载安装：

```shell
docker pull xilinx/vitis-ai-软件框架-硬件架构:latest
```

**示例**:
- **PyTorch CPU-only docker:** `docker pull xilinx/vitis-ai-pytorch-cpu:latest`


- **PyTorch ROCm docker:** `docker pull xilinx/vitis-ai-pytorch-rocm:latest`

- **TensorFlow 2 CPU docker :** `docker pull xilinx/vitis-ai-tensorflow2-cpu:latest`

- **TensorFlow 2 ROCm docker:** `docker pull xilinx/vitis-ai-tensorflow2-rocm:latest`

#### 🟥 选项 2：本地编译 Vitis-AI Docker

| 硬件架构参数 (-t)  | 软件框架参数 (-f)      | 命令参数选择的docker所包含工具                   |
| :--------------- | :-------------------- | :-----------------------------------------  |
| cpu              | pytorch               | `PyTorch（仅CPU版本）`                        |
|                  | tf2                   | `TensorFlow 2 （仅CPU版本）`                  |
|                  | tf1                   | `TensorFlow 1.15 （仅CPU版本）`               |
|                  |                       |                                             |
| gpu              | pytorch               | `PyTorch`     `AI Optimizer` `CUDA-gpu`     |
|                  | tf2                   | `TensorFlow 2` `AI Optimizer` `CUDA-gpu`    |
|                  | tf1                   | `TensorFlow 1.15` `AI Optimizer` `CUDA-gpu` |
|                  |                       |                                             |
| rocm             | pytorch               | `PyTorch` `AI Optimizer` `ROCm-gpu`         |
|                  | tf2                   | `TensorFlow 2` `AI Optimizer` `ROCm-gpu`    |

进入路径`$VITIS_AI_HOME/docker`，根据上方表格选择参数，选择自己所需的docker进行编译安装：

```shell
./docker_build.sh -t 硬件架构参数 -f 软件框架参数
```

在本教程演示中，**硬件架构参数**选择`gpu`，**软件框架参数**选择`pytorch`，以此为例，指令如下所示：
```shell
cd $VITIS_AI_HOME/docker
./docker_build.sh -t gpu -f pytorch
```

>✅ 安装过程完成后如果在末尾处看到类似于如下信息，则表示安装成功:
>```shell
>... ...
>... ...
>[+] Building 630.9s (10/12)                                                                                                   docker:default
>[+] Building 1609.4s (13/13) FINISHED                                                                                         docker:default
> => [internal] load build definition from vitis-ai-cpu.Dockerfile                                                                       0.0s
> => => transferring dockerfile: 1.38kB                                                                                                  0.0s
> => [internal] load .dockerignore                                                                                                       0.0s
> => => transferring context: 2B                                                                                                         0.0s
> => [internal] load metadata for docker.io/xilinx/vitis-ai-gpu-pytorch-base:latest                                                      0.0s
> => [1/8] FROM docker.io/xilinx/vitis-ai-gpu-pytorch-base                                                                               0.0s
> => [internal] load build context                                                                                                       0.0s
> => => transferring context: 11.42kB                                                                                                    0.0s
> => CACHED [2/8] WORKDIR /workspace                                                                                                     0.0s
> => CACHED [3/8] ADD ./common/ .                                                                                                        0.0s
> => CACHED [4/8] ADD ./conda /scratch                                                                                                   0.0s
> => CACHED [5/8] ADD conda/banner.sh /etc/                                                                                              0.0s
> => CACHED [6/8] ADD conda/gpu_conda/bashrc /etc/bash.bashrc                                                                            0.0s
> => [7/8] RUN if [[ -n "pytorch" ]]; then  bash ./install_pytorch.sh; fi                                                             1200.3s
> => [8/8] RUN mkdir -p /opt/vitis_ai/conda/pkgs && chmod 777 /opt/vitis_ai/conda/pkgs && ./install_vairuntime.sh && rm -fr ./*        345.7s 
> => exporting to image                                                                                                                 63.3s 
> => => exporting layers                                                                                                                63.3s 
> => => writing image sha256:a49887360efe4ab69248b0474209f1b7db139e0768932801da82d336a8278e1d                                            0.0s 
> => => naming to docker.io/xilinx/vitis-ai-pytorch-gpu:3.5.0.001-bbccde60d  
>```