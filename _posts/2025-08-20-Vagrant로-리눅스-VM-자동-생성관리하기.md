---
layout: post
title: "Vagrant로 리눅스 VM 자동 생성·관리하기"
date: 2025-08-20T05:08:42.357Z
categories:
  - DevOps
---

## 1. Vagrant란 무엇인가?

### VM 생성을 단순화하는 도구

Vagrant는 **VirtualBox 위에서 VM을 손쉽게 실행·관리할 수 있는 도구**입니다.  
리눅스 CLI를 통해 VM **생성, 삭제, 실행, 종료** 등을 명령어로 제어할 수 있습니다.

### Vagrant Box 개념 (미리 만들어진 OS 이미지)
Vagrant Box는 **리눅스 설치에 필요한 설정과 프로그램을 하나의 이미지로 묶어 경량화한 형태**입니다.
따라서 Box를 이용하면 직접 OS를 설치하지 않고도 쉽게 VM을 만들 수 있습니다.

👉 Vagrant Box는 [Vagrant Cloud](https://portal.cloud.hashicorp.com/vagrant/discover?query=centos%209)에서 다운로드할 수 있습니다.

### VirtualBox와의 관계 (하이퍼바이저 필요성)
Vagrant 자체는 가상화 기능이 없기 때문에, **VirtualBox 같은 하이퍼바이저 위에서 실행**됩니다.  
즉, VirtualBox 설치 및 설정이 반드시 필요합니다.

---

## 2. Vagrant 기본 명령어 정리

### VM 수명주기 관리
| 명령어 | 설명 |
| ------ | ---- |
| `vagrant up` | VM 실행 |
| `vagrant halt` | VM 종료 |
| `vagrant reload` | VM 재시작 |
| `vagrant destroy` | VM 삭제 |

### 접속 및 상태 확인
| 명령어 | 설명 |
| ------ | ---- |
| `vagrant ssh` | VM 내부로 SSH 접속 |
| `vagrant box list` | 설치된 Box 목록 확인 |
| `vagrant global-status` | 현재 PC에서 실행 중인 모든 VM 상태 확인 |

### Vagrantfile 생성
원하는 Box 이름(예: `ubuntu/focal64`)을 Vagrant Cloud에서 복사 후 아래 명령어 실행:
[Vargrant cloud](https://portal.cloud.hashicorp.com/vagrant/discover?query=centos%209)에서 centos,ubuntu 등의 이름을 복사해옵니다.
![](https://velog.velcdn.com/images/duwnstj12/post/ae638c94-0ce0-4453-9a3e-2a358b02c0a5/image.png)

```bash
vagrant init ubuntu/focal64 
```text
이 명령어는 vagrant box 첫 세팅을 하는 명령어입니다.
📌 실행 후 `ls` 명령어로 `Vagrantfile` 생성 여부를 확인합니다.


## 3. 작업 디렉토리 구조와 Vagrantfile
프로젝트별로 디렉토리를 구성하며, VM 환경 설정은 **Vagrantfile**에 정의됩니다.
👉 Vagrantfile은 VM 생성·실행을 위한 핵심 설정 파일입니다.

## 4. VM 생성 및 실행 순서 예시 (CentOS & Ubuntu)
1. Box 다운로드
2. VM 생성 (**vagrant up**)
3. SSH 접속 (**vagrant ssh**)
4. 작업 완료 후 VM 종료 (**vagrant halt**)

## 5. 실무에서 자주 겪는 주의사항

- Hyper-V, WSL2, VM Platform과 충돌 가능 → VirtualBox만 활성화 필요
- VirtualBox GUI 직접 조작 금지 → CLI(vagrant 명령어)만 사용할 것
- VPN·백신·네트워크 문제로 Box 다운로드 실패 발생 가능
- 안전한 종료 습관: 반드시 vagrant halt 후 PC 종료