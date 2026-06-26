---
layout: post
title: "[실습]🌐 Vagrant Provisioning으로 자동화된 VM 환경 구축하기"
date: 2025-08-20T09:03:47.009Z
categories:
  - Tech Log
tags:
  - VM머신
---

## 1. Vagrant Provisioning 개요

- Vagrant Provisioning은 **VM 생성 시 자동으로 실행되는 스크립트 기능**입니다.
- 보통 패키지 설치, 서비스 구동, 환경 변수 세팅 등 초기 설정을 자동화할 때 활용합니다.
- 개발 환경을 여러 번 반복해서 만들더라도 **동일한 설정**을 유지할 수 있다는 장점이 있습니다.

---
## 2. Vagrantfile에서 Provisioner 추가하기
`Vagrantfile` 안에 `provision` 블록을 추가하여 설치 및 실행할 명령어를 정의할 수 있습니다.

``` ruby
 config.vm.provision "shell", inline: <<-SHELL
    yum install -y httpd
    systemctl start httpd
    systemctl enable httpd
  SHELL
end
```text
📌 위 예시는 **VM 생성 시 Apache 웹 서버(httpd)를 자동 설치 및 실행**하도록 설정한 코드입니다.

---
## 3. VM 생성 시 프로비저닝 실행 (`vagrant up`)
``` bash
vagrant up
```text
- VM이 처음 생성될 때 `provision` 블록에 정의된 명령어가 자동 실행됩니다.
- 만약 VM이 이미 생성되어 있다면, `up` 시에는 **프로비저닝이 재실행되지 않습니다**.

---

## 4. 실행된 명령어 결과 확인 (파일 출력 예시)
예를 들어 Apache 웹서버가 제대로 설치되었는지 확인하려면 다음 명령어를 실행합니다:
``` bash
cat /etc/os-release
systemctl status httpd
```text
- systemctl status httpd로 웹서버 실행 여부를 확인할 수 있습니다.
- 브라우저에서 http://localhost:8080 (포트 포워딩 시) 접속해도 확인 가능합니다.

---

## 5. 기존 VM에서 프로비저닝 다시 실행하기
- 이미 실행 중인 VM에서 프로비저닝을 다시 실행하려면:
``` bash
vagrant provision

```text
- 또는 `up` 명령어와 함께 옵션을 붙여 실행할 수도 있습니다:
``` bash
vagrant up --provision

```text
⚠️ 단,** Provisioning**은 처음 환경 세팅을 자동화하기 위한 용도이므로, 재실행보다는** Ansible, Puppet 같은 별도 툴**을 쓰는 게 더 바람직합니다.
## 6. Apache 웹서버 자동 설치/구동 예제
1. 패키지 설치 (`yum install -y httpd`)
2. 서비스 실행 (`systemctl start httpd`)
3. 서비스 자동 실행 등록 (`systemctl enable httpd`)
4. 브라우저에서 접속 확인 (`http://localhost:8080`)
    
## 7. 실무 활용 사례
- 초기 환경 세팅 자동화

  - 공통 패키지 설치, 계정/권한 세팅 등 반복 작업을 자동화

- 반복되는 설정 스크립트 관리

  - **Vagrantfile**에 코드로 정의해두면, 같은 설정을 누구나 동일하게 재현 가능

- 테스트 환경 신속 구축

  - 새로운 기능 테스트를 위한 VM을 몇 초 만에 동일 환경으로 재생성 가능