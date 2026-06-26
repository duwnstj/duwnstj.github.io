---
layout: post
title: "[실습]🖥️ Windows에서 VirtualBox로 CentOS VM 만들고 SSH 접속하기"
date: 2025-08-13T14:06:35.102Z
categories:
  - Tech Log
tags:
  - vm
---

CentOS를 직접 설치한 뒤, SSH로 원격 접속하는 전 과정을 정리했습니다.

## 1. 설치 전에 준비할 것
### 1.1 BIOS에서 가상화 켜기
**VirtualBox**에서 리눅스를 구동하려면 가상화 기능(VT-x/AMD-V)이 켜져 있어야 합니다.
부팅 시 **ESC, F2, F10, F12, Del** 중 하나를 눌러 BIOS에 진입하세요.
**Intel Virtualization Technology (VT-x)** 또는 **AMD-V** 항목을 찾아** Enabled**로 변경합니다.
저장 후 재부팅합니다.

---

### 1.2 Windows 기능에서 Hyper-V 끄기
1.2 Windows 기능에서 Hyper-V 끄기
Hyper-V 관련 기능이 활성화되어 있으면 VirtualBox와 충돌합니다.
시작 메뉴에서 **"Windows 기능 켜기/끄기"**를 열고 아래 항목의 체크를 해제합니다.
- Linux용 Windows 하위 시스템 (WSL)
- Windows 하이퍼바이저 플랫폼
- 가상 머신 플랫폼
- Microsoft Hyper-V

> 💡 변경 후 반드시 재부팅하세요.

---

### 1.3 네트워크 충돌 방지 팁
가끔 네트워크가 꼬이는 경우가 있습니다.
이럴 땐 **PC 전원 종료 → 공유기 재부팅 → PC 재부팅 순서**로 진행하면 안정적입니다

---

## 2. VirtualBox에서 CentOS VM 만들기
### 2.1 VM 생성
VirtualBox 실행 후 새로 만들기를 클릭하고 아래처럼 설정합니다.

- 이름: `centosvm`
- 유형: Linux → Red Hat(64-bit)
- 메모리: 2GB
- CPU: 2개
- 디스크: 동적 할당 20GB
> 📷 VM 생성 화면
![](https://velog.velcdn.com/images/duwnstj12/post/ebeb2dfe-ee84-4a52-b5d1-3aed8cbf8534/image.png)

---
### 2.2 CentOS ISO 다운로드 및 연결
CentOS Stream 9 이미지를 [vargarntCloud](https://portal.cloud.hashicorp.com/vagrant/discover?query=centos%209)에서 다운로드합니다.

> 📷 CentOS Stream 9 이미지 
![](https://velog.velcdn.com/images/duwnstj12/post/b909a7ee-60da-42e8-bfd9-8507725820c2/image.png)

다운로드한 **ISO**를 VirtualBox에서
**저장소 → 컨트롤러: IDE → 디스크 선택 → ISO 파일 선택**으로 연결합니다

---

### 2.3 네트워크 어댑터 설정
네트워크는 **NAT + 브리지 어댑터 조합**을 사용합니다.

- 어댑터 1: NAT → VM이 인터넷에 접속 가능
- 어댑터 2: 브리지 어댑터 → 현재 PC 네트워크 어댑터 선택,**케이블 연결됨 체크**
> 📷 어댑터 1 (NAT)
![](https://velog.velcdn.com/images/duwnstj12/post/65dde08d-e16e-43c8-881e-60a1ed507502/image.png)

> 📷 어댑터 2 (브리지)
![](https://velog.velcdn.com/images/duwnstj12/post/7754c4ca-c0bd-494c-9bd7-2e671f64a879/image.png)

---

### 2.4 설치 과정
1. 설치 디스크: 자동 파티션 선택
2. root 계정 비밀번호 설정
3. 포인팅 장치를 USB Tablet으로 변경 → 마우스 반응 개선

### 2.5 ISO 제거
설치가 끝나면 ISO를 제거해야 합니다.
그대로 두면 재부팅 시 다시 설치 화면이 뜹니다.
**저장소 → ISO 선택 → "가상 드라이브에서 디스크 제거"**로 처리합니다.

---
## 3. CentOS VM에 SSH 접속하기
### 3.1 IP 주소 확인
VM 실행 후 root 로그인 → IP 확인:

``` bash
ip addr show

```text
브리지 어댑터로 연결된 인터페이스의 IP를 사용합니다
> 📷 명령어 실행 결과 (빨간 네모부분이 브리지 IP)
![](https://velog.velcdn.com/images/duwnstj12/post/48814bd3-8154-457d-9b11-6527df104e7e/image.png)

---

### 3.2 Git Bash에서 SSH 접속
Windows에서 Git Bash 또는 터미널을 열고:

``` bash
ssh centosuser@192.168.219.103
```text
- `centosuser`는 설치 시 만든 계정명입니다.
- IP 주소는 3.1에서 확인한 브리지 IP를 사용합니다.
- 비밀번호 입력 시 화면에 표시되지 않지만 입력되고 있는 것입니다.

> 📷 SSH 접속완료
![](https://velog.velcdn.com/images/duwnstj12/post/c6f42f0f-97fa-4570-ac72-1dfc4da4638d/image.png)

---

## 4. 마무리
이제 SSH로 CentOS 서버에 접속할 수 있습니다.
추가로 패키지 설치, 방화벽 설정, 사용자 계정 관리 등 리눅스 명령어를 연습하면 됩니다.