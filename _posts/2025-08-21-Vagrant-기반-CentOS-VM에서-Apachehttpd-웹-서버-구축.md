---
layout: post
title: "[실습]🖥️ Vagrant 기반 CentOS VM에서 Apache(httpd) 웹 서버 구축"
date: 2025-08-21T03:42:54.650Z
categories:
  - DevOps
---

## 1. 서버 관리 개요

**httpd(Apache HTTP Server):** 리눅스에서 가장 널리 쓰이는 웹 서버.

**apache2**: **Ubuntu/Debian** 계열에서 쓰이는 패키지명. CentOS/RedHat 계열에서는** httpd**라는 이름으로 제공됨.

👉 따라서 **운영체제에 따라 명령어가 달라질 수 있음**을 주의해야 합니다.

---
## 2. Vagrant VM 준비
### 네트워크 설정 : 
``` bash
  config.vm.network "private_network", ip: "192.168.56.21"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  config.vm.network "public_network"

```
- ** private_network**: 호스트 전용 네트워크 (개발용 내부 테스트에 주로 사용)

- **public_network**: 브리지 네트워크. VM이 물리 네트워크 상의 별도 장비처럼 동작

### 메모리 및 CPU 설정
``` bash
 config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
   vb.memory = "1024"
   vb.cpus = 2
  end

```
### 프로비저닝 설정 (httpd 자동 설치) :
``` bash
 config.vm.provision "shell", inline: <<-SHELL
      # 패키지 설치
      dnf install httpd -y
      systemctl start httpd
      systemctl enable httpd
  SHELL

```
- VM이 처음 실행될 때 자동으로 `httpd`가 설치되고 실행됨

--- 
## 3. httpd 설치 및 서비스 실행
 
   ``` bash
   systemctl status httpd
```
### 출력 예시 :
``` bash
Active: active (running) since ...

```
  👉 active `(running)` 상태라면 정상적으로 실행 중
  ---
## 4. 기본 index.html 테스트 페이지 생성
- Apache(httpd) 웹 루트 디렉토리: /var/www/html
- 여기에 `index.html` 파일을 생성하면 브라우저에서 확인 가능

``` bash
dnf install vim unzip zip -y
```
- vim: 파일 편집기
- unzip/zip: 템플릿 압축 해제 및 관리

---
## 5. Tooplate 템플릿 다운로드 및 배포
### 1. 브라우저(Brave 등)에서 다운로드 링크 확인

[Tooplate](https://www.tooplate.com/) 사이트에서 원하는 템플릿 다운로드 URL 확보
  - 다운로드를 클릭한 후 다운로드 URL은 F12(개발자모드)에서 확인할 수 있습니다. 
![](https://velog.velcdn.com/images/duwnstj12/post/6802ec3e-bffc-4b64-8658-1d5bdbfb41a5/image.png)

### 2. wget으로 다운로드
``` bash
wget <다운로드_URL>
```
![](https://velog.velcdn.com/images/duwnstj12/post/1e4b6d17-3a0c-4e52-989d-905d97ee8c75/image.png)

### 3. 압축 해제
``` bash
unzip template.zip
```
### 4. 웹 루트 디렉토리로 복사
``` bash
sudo cp -r template/* /var/www/html/
```
---

### 5. 카피 결과
``` bash
[root@vbox ~]# ls
2133_moso_interior  2133_moso_interior.zip  anaconda-ks.cfg  original-ks.cfg
[root@vbox ~]# cp -r 2133_moso_interior/* /var/www/html
cp: overwrite '/var/www/html/index.html'? yes
[root@vbox ~]# ls /var/www/html
'ABOUT THIS TEMPLATE.txt'   fonts    index.html   shop-detail.html
 css                        images   js           shop-listing.html
[root@vbox ~]#

```
## 6. 방화벽(firewalld) 상태 확인 및 해제(실습 환경)
### 실습 편의상 방화벽 해제:
``` bash
systemctl stop firewalld
systemctl disable firewalld

```
👉 실제 운영환경에서는 반드시 방화벽 규칙으로 **80포트**만 허용해야 함.

---
## 브라우저에서 결과 확인

### VM의 IP 주소 확인:

``` bash
ip addr show

```
![](https://velog.velcdn.com/images/duwnstj12/post/b1db80bc-651e-4f7a-af18-1a98cef7139a/image.png)
이 주소가 public(bridge) 주소
### 브라우저 접속
```text
http://192.168.56.21

```
### 결과
![](https://velog.velcdn.com/images/duwnstj12/post/5f5fcbb4-9bde-43f9-a784-40e149f25ca1/image.png)

- 정상적으로 index.html 또는 템플릿 페이지가 출력되면 구축 성공 🎉