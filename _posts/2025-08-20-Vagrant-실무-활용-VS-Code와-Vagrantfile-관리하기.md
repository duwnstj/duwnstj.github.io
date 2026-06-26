---
layout: post
title: "[실습]Vagrant 실무 활용: VS Code와 Vagrantfile 관리하기"
date: 2025-08-20T08:43:07.611Z
---

## 1. **Vagrantfile 개요**

- Vagrantfile은 **가상 머신(VM)의 모든 설정을 코드로 정의**하는 파일입니다.
- Ruby 기반 DSL을 사용하며, 기본 구조는 다음과 같습니다:
``` ruby
Vagrant.configure("2") do |config|
  # VM 설정 정의
end

```
- `#` 기호를 사용하여 주석을 추가할 수 있으며, 실험 중인 설정을 관리할 때도 유용합니다.

---

## 2. **VS Code 환경 설정**
- Vagrantfile 작업을 편하게 하기 위해 **VS Code**에서 환경을 세팅하는 것이 좋습니다.
  - 기본 터미널 설정
    - Windows: Git Bash
    - macOS/Linux: 기본 터미널
- **Vagrantfile Extension 설치**
  - Vagrantfile 전용 문법 하이라이팅 지원
  - JSON이나 YAML과 달리 Ruby 문법 기반이므로 가독성 향상 가능
  ---
## 3. **Vagrantfile 기본 설정 항목**
   | 설정 항목                | 설명             | 예시                                  |
| -------------------- | -------------- | ----------------------------------- |
| `config.vm.box`      | 사용할 Box 이미지 지정 | `"centos/7"`                        |
| `config.vm.hostname` | VM의 호스트명 설정    | `"my-vm"`                           |
| `config.vm.network`  | 네트워크 방식 지정     | `public_network`, `private_network` |
| `config.vm.provider` | 하이퍼바이저별 세부 옵션  | VirtualBox 설정 블록                    |

## 4. **실습: Vagrantfile 다루기**
기존 Vagrantfile 열기 → 필요한 설정 주석 해제 및 수정
![](https://velog.velcdn.com/images/duwnstj12/post/39513fdb-9f7c-4e98-95e7-278d45724ad8/image.png)
![](https://velog.velcdn.com/images/duwnstj12/post/cfaca745-bf55-43d5-9f8c-a7cc5380c719/image.png)

네트워크 설정 후 vm 박스의 memory를 설정해주었습니다.

변경 사항 반영:

``` bash
vagrant reload
```


VM 상태 확인:

``` bash
vagrant status
```


 

---
## 5. **여러 VM 디렉토리 관리하기**
- VM을 프로젝트별로 관리하는 것이 일반적입니다.
  - 예시 디렉토리 구조:
  
``` markdown
vagrant-vms/
├── centos/
│   └── Vagrantfile
└── ubuntu/
    └── Vagrantfile

```
- 전역 상태 확인:
``` bash
vagrant global-status
```
- 오래된 캐시 정리:
```
vagrant global-status --prune

```

## 📌 정리

Vagrantfile은 VM 환경을 코드로 선언하고 관리할 수 있는 핵심 파일입니다.

- 코드 기반 설정 → 환경 재현성 확보
- 네트워크, CPU, 메모리, 스토리지까지 세밀하게 제어 가능
- global-status와 디렉토리 기반 관리로 프로젝트별 VM을 깔끔하게 운영
👉 결국 DevOps 관점에서 **Vagrantfile은 ‘인프라를 코드로 다루는 첫걸음’**이라 할 수 있습니다.
