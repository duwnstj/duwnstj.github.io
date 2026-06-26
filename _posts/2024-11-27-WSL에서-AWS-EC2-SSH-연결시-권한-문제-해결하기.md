---
layout: post
title: "WSL에서 AWS EC2 SSH 연결시 권한 문제 해결하기"
date: 2024-11-27T12:21:46.314Z
categories:
  - Cloud
tags:
  - 트러블 슈팅
---

AWS EC2에 SSH로 접속하려할 때 이러한 에러가 뜨게 되었습니다.

![](https://velog.velcdn.com/images/duwnstj12/post/f74fa36e-1b74-41a4-aeab-938d70522cb0/image.png)
이 에러는 **프라이빗 키 파일의 권한이 너무 넓게 열려 있어서** 발생합니다. 특히, WSL(Windows Subsystem for Linux) 환경에서 **NTFS 파일 시스템의 특성**으로 인해 이러한 문제가 더 자주 발생합니다.
이번 글에서는 **문제의 원인과 해결 방법**을 단계별로 알아보겠습니다.

## 1. 문제의 원인
AWS EC2는 보안을 위해 **프라이빗 키 파일(.pem)**이 사용자 본인만 접근 가능하도록 설정되어야 합니다. 하지만 **WSL**에서는 다음과 같은 이유로 문제가 발생할 수 있습니다.
1. **NTFS 파일 시스템의 특성**:

- NTFS는 **ACL(Access Control List)** 기반으로 동작하며, Linux의 Unix 스타일 권한 체계(`chmod, chown`)를 완벽히 지원하지 않습니다.
- WSL에서 NTFS 파일에 대해 `chmod` 명령어를 실행하더라도 실제 권한이 변경되지 않거나 SSH에서 이를 제대로 인식하지 못할 수 있습니다.

2. **SSH의 보안 정책** 
- 프라이빗 키 파일의 권한이 너무 열려 있으면 SSH는 이를 무시하고 접속을 차단합니다.


## 2. 해결 방법

### 2-1 : 파일을 WSL의 홈 디렉토리로 이동

WSL에서 권한 변경이 제대로 작동하려면 `.pem` 파일을 Linux 파일 시스템(홈 디렉토리)로 이동해야합니다.

![](https://velog.velcdn.com/images/duwnstj12/post/f5ff934e-bf0c-4988-aa3d-f2774f5070db/image.png)
- `mv` : 현재 경로에 있는 `keyPiar.pem`파일을 홈 디렉토리로 이동 
    - 여기서 `~가 홈 디렉토리`를 말합니다.
- `cd ~` : 홈 디렉토리로 이동합니다.

### 2-2 : 파일 권한 수정
홈 디렉토리로 이동한 `.pem` 파일에 권한을 설정합니다.
![](https://velog.velcdn.com/images/duwnstj12/post/24253ee2-79cd-4cd3-a955-24cfb21d15cd/image.png)
- **400 권한** : 사용자(owner)만 읽기`r` 권한을 가지며 그룹 및 다른 사용자들은 접근할 수 없습니다.
- **왜 필요하지?**
    - SSH는 보안을 위해 프라이빗 키 파일이 사용자 본인 외에는 접근할 수 없도록 설정되어야만 작동합니다.
    
### 2-3 : 파일 권한 확인 
권한 설정 후 `.pem` 파일의 권한이 적절히 설정되었는지 확인합니다.
- **명령어** : `ls -l keyPiar.pem`
    - 이 명령어는 파일의 권한,소유자,크기,수정 시간을 확인합니다.
- **출력 결과** : 
`-r-------- 1 root root 1678 Nov 27 19:08 keyPiar.pem`
- `r` : 소유자만 읽기`r` 권한을 가지며 그룹과 다른 사용자에게는 접근이 불가능합니다.

### 2-4 : SSH 연결 시도
권한을 수정한 후 SSH를 통해 EC2 인스턴스에 접속할 수 있는지 테스트합니다.
- **명령어** : ![](https://velog.velcdn.com/images/duwnstj12/post/adc43638-6d57-4984-94d0-bb029533efb3/image.png)
- `-i` : 인증에 사용할 프라이빗 키 파일 경로를 지정
- `ubuntu@<EC2_public_IP>` : 접속할 사용자 `ubuntu`와 퍼블릭 IP 주소

## 결과
아래와 같이 정상적으로 EC2에 접속되면 문제 해결 완료된것입니다 ! 
![](https://velog.velcdn.com/images/duwnstj12/post/4500c67d-d5dc-4b3a-bb3b-e530499417fb/image.png)

## 3. NTFS 경로에서도 작동ㅇ하게 하기 
WSL 설정을 변경하면 NTFS 경로(/mnt/c/...)에 있는 `.pem`파일도 사용할 수 있습니다.

### 3-1 : WSL 설정 변경
WSL의 설정 파일(`/etc/wsl.conf`)에 아래 내용을 추가해 Unix 스타일 권한 관리를 활성화합니다.

1. **설정 파일 열기**

```bash
sudo nano /etc/wsl.conf
```text
2. **내용 추가**
```ini
[automount]
options = "metadata"
```text
3. **파일 저장** 
- `Ctrl+O` : 저장
- `Enter` : 저장 확정
- `Ctrl + X` : 편집기 종료

### 3-2 WSL 재시작
설정을 적용하려면 WSL을 재시작합니다.

**명령어**

```bash
wsl --shutdown
wsl

```text
**결과** : 이제 NTFS 파일 시스템에서도 `chmod` 명령이 정상적으로 작동합니다. 







