---
layout: post
title: "[실습]S3 → EC2로 Spring Boot 멀티모듈 배포 (Docker 적용 전)"
date: 2025-10-16T10:59:01.111Z
---


## 1️⃣ 목표 및 구성 개요

이번에는 **Spring Boot 멀티모듈 프로젝트를 AWS 환경에 직접 배포**했습니다.

Docker로 컨테이너화하기 전,

먼저 **S3를 빌드 산출물 저장소**, **EC2를 실행 환경**으로 구성했습니다.

현재는 **로드 밸런서(ALB)** 없이 단일 EC2에서 동작 중이며,

추후 Docker 전환 시 **Nginx 프록시 라우팅 구조**로 교체할 예정입니다.

### ⚙️ 구성 요약

| 구성 요소 | 역할 |
| --- | --- |
| EC2 (Ubuntu 24.04) | 인바운드 80(전체), 22(내 IP) |
| S3 버킷 | 빌드된 `.jar` 업로드 및 다운로드 |
| IAM 사용자 | 로컬 → S3 업로드 권한 |
| IAM 역할(Role) | EC2 → S3 다운로드 권한 |
| 결과 요약 | ✅ 웹 서버 정상 기동 / ⚠️ DB 연결은 로컬 설정으로 실패 |

---

## 2️⃣ 사전 구성 (보안그룹 · 키페어 · IAM · S3)

### ✅ 보안그룹 설정

**인바운드**

- HTTP (80): Anywhere (0.0.0.0/0)
- SSH (22): My IP

**아웃바운드**

- 전체 허용 (S3, 패키지 설치용 통신 필요)

---

### ✅ 키페어 생성

- EC2 SSH 접속용 키페어를 생성하고 `.pem` 파일을 로컬에 다운로드.
- ⚠️ 이 키는 절대 깃허브 등 외부 저장소에 업로드하지 않도록 주의.

---

### ✅ S3 + IAM 사용자 (로컬 업로드용)

1. **S3 버킷 생성**
    - 예: `shoesorder-artifacts`
2. **IAM 사용자 생성**
    - 이름: `shoesorder-s3-admin`
    - 권한: `AmazonS3FullAccess`
    - 액세스 키/시크릿 키 발급 후 CSV로 저장
3. **로컬 CLI 인증 등록**
    
    ```bash
    aws configure
    
    ```
    
    - Access Key / Secret Key / Region / Output Format 입력
    - 저장 위치: `~/.aws/credentials`, `~/.aws/config`

💡 예전에는 `.env` 파일에 키를 저장하고 `.gitignore`로 관리했지만,

실수로 유출될 가능성이 있어 **CLI 자격증명 방식**으로 전환했습니다.

---

### ✅ IAM 역할 (EC2 → S3 다운로드용)

- IAM Role 생성
    - 신뢰 주체: EC2
    - 권한: `AmazonS3FullAccess`
- EC2 인스턴스에 Role 연결
    - 콘솔 → EC2 선택 → **Actions → Security → Modify IAM Role**

➡️ 이렇게 하면 EC2 내부에서 **별도의 키 파일 없이** `aws s3 cp` 명령으로 S3 파일을 바로 가져올 수 있습니다.

---

## 3️⃣ 로컬 빌드 및 S3 업로드

### 🔧 빌드 전 준비

**필수 도구**

- JDK 17
- Gradle (Wrapper 권장)
- AWS CLI

**실행 모듈 설정**

```
bootJar.enabled = true
jar.enabled = false

```

> 실행 가능한 JAR을 만들기 위해 bootJar를 활성화합니다.
> 
> 
> (plain.jar는 라이브러리 전용)
> 

---

### 🧱 빌드

실행 모듈 `module-owner` 기준

```bash
./gradlew build

```

- 산출물: `module-owner/build/libs/module-owner-0.0.1-SNAPSHOT.jar`

---

### ☁️ S3 업로드

```bash
aws s3 cp module-owner/build/libs/module-owner-0.0.1-SNAPSHOT.jar s3://shoesorder-artifacts/

```

업로드 결과 확인:

```bash
aws s3 ls s3://shoesorder-artifacts/

```

✅ 정상 업로드 완료

![](https://velog.velcdn.com/images/duwnstj12/post/8849446f-561c-4ccb-bd2f-d561666de401/image.png)

---

## 4️⃣ EC2에서 JAR 다운로드 및 실행

### ☕ Java 설치

```bash
sudo apt update -y
sudo apt install -y openjdk-17-jdk
java -version

```

> java 명령어 사용을 위해 JDK 17을 설치합니다.
> 

---

### 📂 애플리케이션 디렉터리 구성

```bash
mkdir -p /home/ubuntu/app
aws s3 cp s3://shoesorder-artifacts/module-owner-0.0.1-SNAPSHOT.jar /home/ubuntu/app/
ls -lh /home/ubuntu/app

```

---

### ▶ 애플리케이션 실행

```bash
java -jar /home/ubuntu/app/module-owner-0.0.1-SNAPSHOT.jar

```

- 포트: `application.yml` 설정 기준 (예: `server.port=8081`)
- 접속: `http://<EC2_Public_IP>:8081`

---

## 5️⃣ 실행 로그 점검 (웹 ✅ / DB ⚠️)

### ✅ 정상 동작 로그

- Spring Boot 배너 출력
- 내장 톰캣 초기화 완료
- 웹 서버 정상 기동

---

### ⚠️ DB 연결 실패 로그

```bash
Communications link failure
Connection refused
Unable to determine Dialect without JDBC metadata

```

### 원인 분석

- DB 설정이 `127.0.0.1` (로컬)로 되어 있음
- EC2에서 실행 중이므로 RDS 또는 EC2-MySQL의
    
    **프라이빗 IP 혹은 내부 DNS**로 연결해야 함
    

### 보안그룹 설정 확인

- DB SG 인바운드: `3306/TCP`
- 소스: App SG (IP 기반이 아닌 SG 참조 방식)

---

### 로그 해석 요약

| 로그 | 의미 |
| --- | --- |
| `Communications link failure` | DB 네트워크 연결 자체 실패 |
| `Unable to determine Dialect...` | JDBC 메타데이터를 읽지 못함 (DB 미연결 상태) |

---

### 현재 상태 요약

| 항목 | 상태 | 설명 |
| --- | --- | --- |
| 웹 서버 | ✅ 정상 | S3 → EC2 배포 성공 |
| DB 연결 | ⚠️ 실패 | 로컬(127.0.0.1) 연결로 인해 통신 불가 |

---

## 🔚 마무리 및 적용 후기

이번 과정은 **내 프로젝트를 AWS 환경에 실제 배포**해보면서,

S3를 아티팩트 저장소로, EC2를 런타임 환경으로 사용하는 구조를 직접 검증한 작업이었습니다.

Docker처럼 자동화된 빌드·배포는 아니지만, 이 과정을 통해 AWS 인프라의 기본 흐름을 체득할 수 있었습니다.

---

### 🧩 이번 구성에서 배운 점

✅ IAM Role 기반 접근 제어의 중요성

✅ S3 → EC2 아티팩트 전달 파이프라인 구성 방식

✅ Spring Boot JAR의 실제 실행 및 로그 분석

> “자동화 전에 수동으로 과정을 완전히 이해하는 것”
> 
> 
> 이게 진짜 DevOps의 첫걸음이라고 느꼈습니다.
>