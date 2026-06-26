---
layout: post
title: "[Docker/Spring Boot] gradlew 부재부터 포트 충돌까지: 원리 중심으로 정면 돌파한 로컬 인프라 구축기"
date: 2026-06-12T15:40:37.884Z
---


## 1. 개요 및 문제 상황 (Situation & Problem)

새로운 커버곡 챌린지 플랫폼 프로젝트의 백엔드 뼈대 코드를 빌드하고, 로컬 환경에서 구동하는 과정에서 연속적인 인프라 장벽에 부딪혔다.

에러를 마주한 순서와 당시 터진 메시지는 다음과 같다.

### 🚨 에러 1. 빌드 실행 파일의 부재

Spring Boot 프로젝트 루트 폴더에서 서버를 가동하려 했으나 실행 파일이 아예 없었다.


```bash
$ ./gradlew bootRun
-bash: ./gradlew: No such file or directory
```

### 🚨 에러 2. 로컬 빌드 엔진(Gradle)의 부재

누락된 래퍼를 생성하기 위해 `gradle wrapper` 명령을 날렸으나, 내 로컬 환경(WSL/Windows)에 Gradle 자체가 없었다.


```bash
$ gradle wrapper
Command 'gradle' not found, but can be installed with:
apt install gradle
```

### 🚨 에러 3. 도커 데몬(Docker Daemon) 미구동

로컬에 억지로 Gradle을 수동 설치하는 대신 Docker를 이용해 우회하려 했으나, 배후의 도커 엔진이 깨어나 있지 않았다.



```PowerShell
PS C:\> docker run --rm gradle:8.7.0-jdk17 gradle wrapper
docker: error during connect: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

## 2. 원인 분석 및 의심 범주 (Analysis)

### 🔍 의심 범주 1: 환경 격리 및 이식성 훼손 위험

에러 2를 만났을 때, 블로그나 구글링에서는 으레 `apt install gradle`이나 Windows 환경 변수 설정을 통해 Gradle을 로컬 PC에 직접 설치하라고 권장한다. 하지만 클라우드/DevOps 관점에서 **로컬 호스트 OS에 무겁게 빌드 엔진을 직접 설치(하드코딩)하는 것은 환경 오염이자 이식성을 떨어뜨리는 행위**라고 판단했다.

### 🔍 의심 범주 2: 호스트와 컨테이너의 세계관 분리

도커파일(`Dockerfile`)을 작성할 때 `WORKDIR /build`나 `WORKDIR /app` 설정을 보며 "내 바탕화면 폴더에는 저런 이름이 없는데 왜 작동하지?"라는 의문이 들었다. 조사 결과, **호스트 PC(Windows)의 파일 시스템과 Docker 컨테이너 내부의 리눅스 파일 시스템은 철저하게 격리된 별개의 세계**임을 깨달았다. `WORKDIR`은 컨테이너 '안' 세상의 작업 공간을 뜻하는 것이었다.

## 3. 해결 과정 및 가설 검증 (Action)

### 🛠️ 해결 1. 로컬 설치 없이 'Docker Volume Mount'로 래퍼 주입

로컬 OS를 더럽히지 않고, **Java 17과 Gradle 8.7이 완벽히 세팅된 공식 Docker 이미지**를 잠깐 빌려와서 래퍼 파일만 내 바탕화면으로 쏙 빼내오는 가설을 세웠다.

Docker Desktop 엔진을 깨운 후, PowerShell에서 아래 명령어를 실행했다.



```PowerShell
docker run --rm -v "${PWD}:/home/gradle/project" -w /home/gradle/project gradle:8.7.0-jdk17 gradle wrapper
```

이 명령어는 호스트(Windows)와 컨테이너(Linux)라는 두 개의 서로 다른 세계관을 연결하는 포탈(워프 게이트)을 여는 핵심 인프라 메커니즘을 담고 있다. 각 옵션의 내부 작동 원리는 다음과 같다.

- **`v "${PWD}:/home/gradle/project"` (볼륨 마운트):** 내 실제 Windows PC의 현재 폴더 경로(`"${PWD}"`)와 `gradle` 공식 이미지(리눅스 기반) 내부에 기본적으로 존재하는 작업 폴더인 `/home/gradle/project`를 실시간 거울처럼 동기화(마운트)한다. 내 호스트 PC에는 저 리눅스 경로가 없지만, 컨테이너가 켜지는 순간 도커 엔진이 두 공간 사이에 실시간 포탈을 생성한다.
- **`w /home/gradle/project` (작업 디렉토리):** 가상 리눅스 컨테이너가 켜지자마자 자동으로 `cd /home/gradle/project`를 수행하여, 내 Windows 소스 코드가 투영되어 있는 그 방으로 걸어 들어가 대기하도록 지시한다.
- **`gradle:8.7.0-jdk17 gradle wrapper` (엔진 실행 및 파일 생성):** 이미지 내부에 이미 설치되어 있던 `gradle`이라는 기술자(빌드 프로그램 엔진)가 깨어나, 현재 서 있는 방(`w`로 들어온 공간)에 `gradlew`, `gradlew.bat` 등의 실행 파일들을 새로 제작(Generate)한다.

**💡 핵심 인프라 인사이트:**
이미지 안에 숨겨져 있던 파일을 단순히 꺼내온 것이 아니다. 컨테이너 안의 Gradle 엔진이 파일을 **새로 생성**한 것이며, 그 공간이 `-v` 옵션 덕분에 내 Windows 폴더와 포탈로 연결되어 있었기 때문에 **호스트 PC 바탕화면에 결과물이 실시간으로 배달되어 툭 떨어지게 된 것**이다. 파일 작성이 끝나면 `--rm` 옵션에 의해 가상 컴퓨터는 흔적도 없이 자동 파기(`-c`)된다.

- **결과:** 호스트 OS의 환경을 단 1%도 오염시키지 않고, 격리된 도커 엔진의 힘만으로 로컬 프로젝트에 Gradle 래퍼를 안전하게 주입하는 데 성공했다.

### 🛠️ 해결 2. FinOps(비용 최적화)를 고려한 '멀티 스테이지 빌드' 도입

생성된 래퍼를 바탕으로, 배포 속도와 AWS ECR/S3 저장소 비용을 극적으로 아낄 수 있는 **멀티 스테이지 빌드(Multi-stage Build)** 방식의 `Dockerfile`을 설계했다.



```Dockerfile
# Stage 1: Build Stage (무거운 빌드 도구가 포함된 방)
FROM gradle:8.7.0-jdk17 AS builder
WORKDIR /build
COPY gradlew settings.gradle build.gradle ./
COPY gradle ./gradle
COPY src ./src
RUN chmod +x ./gradlew
RUN ./gradlew bootJar --no-daemon

# Stage 2: Run Stage (초경량 실행 전용 방)
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
# builder 단계에서 완성된 최종 .jar 파일만 쏙 훔쳐오기 (★FinOps 핵심)
COPY --from=builder /build/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

- **원리:** 컴파일을 수행하는 1번 방(`builder`)의 수백 MB짜리 Gradle 빌드 찌꺼기들을 과감히 버리고, 2번 방(`alpine` 초경량 리눅스 환경)에는 단 몇십 MB짜리 실행 알맹이(`app.jar`)만 이주시켜 **최종 이미지 용량을 최소화**했다.
- **결과:** `docker build -t cover-challenge:1.0 .` 명령을 통해 슬림하고 압축된 첫 도커 이미지 빌드에 성공했다.

### 🛠️ 해결 3. 포트 포워딩을 통한 네트워크 격리성 검증

기존에 `8080` 포트로 가동 중인 본 서버 컨테이너를 유지한 채, 마케팅 팀의 요청으로 테스트용 서버(`my-test-app`)를 한 대 더 추가 구동해야 하는 상황을 가정했다.

호스트 OS(Windows)의 `8080` 포트는 이미 선점당해 충돌이 날 것이 뻔하므로, **포트 포워딩(`-p`) 설정을 변경하는 가설**을 세워 검증했다.



```PowerShell
docker run -d -p 8081:8080 --name my-test-app cover-challenge:1.0
```

- **원리:** 각 컨테이너 내부 웹 사이트(Spring Boot)는 독립된 방에 있으므로 똑같이 내부 포트 `:8080`을 써도 충돌하지 않는다. 대신 외부와 통하는 호스트 PC의 문을 `8081:`로 다르게 열어주어 진입로를 분리했다.
- **결과:** 두 개의 컨테이너가 충돌 없이 동시에 정상 구동되었다.

## 4. 최종 결과 및 배운 점 (Result & Retrospective)

최종적으로 도커 컨테이너를 백그라운드(`-d`)로 실행한 뒤, 브라우저에서 `http://localhost:8080/api/health`를 찔러본 결과, 우리가 설계한 헬스체크 API가 정상적으로 작동함을 확인했다.

![](https://velog.velcdn.com/images/duwnstj12/post/a92799ef-cdec-4558-bb07-fc228e7bb5df/image.png)


### 👨‍🏫 인프라 엔지니어로서의 고찰

1. **운영 환경의 영향과 안정성 (형상 관리):**
만약 빌드할 때 태그명을 귀찮다고 `1.0` 혹은 `latest`로 계속 고정해서 배포한다면, 실무 오케스트레이션 시스템(AWS ECS, Kubernetes)은 변경사항을 감지하지 못하고 구버전 컨테이너를 유지하거나 배포 오염을 일으킬 수 있다. 안정적인 운영을 위해 **Git 커밋 해시**나 **타임스탬프**를 빌드 태그명으로 자동 주입하는 자동화 파이프라인(CI/CD) 도입이 필수적임을 깨달았다.
2. **사전 방지책 (네트워크):**
실무에서는 컨테이너의 `8080` 포트를 인터넷에 날것으로 노출하지 않는다. 앞단에 **Nginx 웹 서버**나 AWS ALB(로드밸런서)를 방패막이로 세워 `80` 또는 `443`으로 통신을 받고, 내부망에서만 도커 컨테이너와 통신하도록 설계해야 보안 사고를 막을 수 있다.
3. **재발 방지책 (모니터링):**
우리가 구현한 `/api/health` 응답은 단순히 개발자 확인용이 아니다. 클라우드 환경에서 로드밸런서가 이 주소를 주기적으로 찔러보게 하여(Health Check), 서버가 뻗었을 때 자동으로 불량 컨테이너를 폐기하고 새 컨테이너를 채우는 자가 치유(Self-Healing)의 근간이 됨을 배웠다.