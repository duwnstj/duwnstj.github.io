---
layout: post
title: "Spring Boot 프로젝트를 Docker 컨테이너로 실행하기"
date: 2026-03-08T04:42:39.611Z
categories:
  - DevOps
---



Dockerfile로 이미지를 만든다는 것은 결국 그 이미지를 컨테이너화해서 실행한다는 의미입니다. 이번에는 실제 Spring Boot 프로젝트를 컨테이너로 실행하면서 마주친 문제들과 해결 과정을 정리했습니다.

---

### 1. 환경변수를 읽지 못하는 문제

컨테이너를 실행하자마자 `PlaceholderResolutionException` 에러가 발생했습니다. 원인은 `.env` 파일을 읽지 못해서였습니다.

GitHub에 올릴 때 `.gitignore`에 `.env` 파일을 추가해두었기 때문에, clone 받은 환경에는 `.env` 파일이 없었습니다. 파일을 다시 생성한 후, `--env-file` 옵션으로 환경변수를 컨테이너에 전달했습니다.


`docker run --env-file .env -p 8081:8081 myapp:good`

| 옵션 | 설명 |
| --- | --- |
| `--env-file .env` | .env 파일의 환경변수를 컨테이너에 주입 |
| `-p 8081:8081` | [호스트 포트]:[컨테이너 포트] 매핑 |

실제 배포 시에는 앞단에 로드밸런서나 Nginx를 두고, 80(HTTP) 또는 443(HTTPS)으로 들어온 요청을 내부 8081 포트로 전달하는 구조를 사용합니다.

---

### 2. DB 연결 실패 문제

환경변수 문제를 해결한 후 다시 실행했더니 이번에는 DB 연결 에러가 발생했습니다.

### 원인 1: localhost의 의미 차이

`.env` 파일에 `DB_LINK=localhost`로 설정되어 있었습니다. 로컬 개발 환경에서는 문제가 없지만, 컨테이너 내부에서 `localhost`는 컨테이너 자신을 가리킵니다.

| 환경 | localhost의 의미 |
| --- | --- |
| 호스트에서 실행 | 호스트 자신 (DB 접근 가능) |
| 컨테이너에서 실행 | 컨테이너 자신 (DB 없음) |

### 원인 2: MySQL 컨테이너 부재

더 근본적인 문제는 Docker 환경에 MySQL 자체가 없었다는 것입니다. 기존에는 Windows OS 위에 MySQL이 설치되어 있었지만, 지금은 VM 안의 Linux OS 위에서 컨테이너가 돌아가는 상황입니다.

{% highlight bash %}
docker run -d --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=비밀번호 \
  -e MYSQL_DATABASE=shoes_order \
  -p 3306:3306 \
  mysql:8`
{% endhighlight %}
| 옵션 | 설명 |
| --- | --- |
| `-d` | 백그라운드 실행 |
| `--name mysql-db` | 컨테이너 이름 지정 |
| `-e` | 환경변수 설정 |

#### 2-1 해결: 컨테이너 네트워크 구성

두 컨테이너가 통신하려면 같은 네트워크에 있어야 합니다.


{% highlight bash %}
# 네트워크 생성
docker network create web-network

{% endhighlight %}
#### 2-2 MySQL 컨테이너를 네트워크에 연결
`docker network connect web-network mysql-db`

#### 2-3 웹 컨테이너 실행 (같은 네트워크)
{% highlight bash %}
docker run --env-file .env --name shoesorder-web \
  --network web-network -p 8081:8081 myapp:good
{% endhighlight %}
| 명령어 | 설명 |
| --- | --- |
| `docker network create` | 사용자 정의 네트워크 생성 |
| `docker network connect` | 실행 중인 컨테이너를 네트워크에 연결 |
| `--network` | 컨테이너 실행 시 네트워크 지정 |

같은 네트워크 안에서는 **컨테이너 이름**으로 서로 접근할 수 있습니다. `.env` 파일을 `DB_LINK=mysql-db`로 수정하면 됩니다.

---

### 3. S3 환경변수 누락 문제

DB 연결이 해결되자 이번에는 S3 관련 에러가 발생했습니다. S3 기능을 실제로 사용하지 않더라도, 앱 시작 시 해당 Bean을 생성하려고 하기 때문에 환경변수가 필요합니다. 일단 더미값을 넣어 해결했습니다.


### 3-1 env 파일에 추가
{% highlight bash %}
`AWS_S3_ACCESS_KEY=dummy
AWS_S3_SECRET_KEY=dummy
AWS_REGION_STATIC=ap-northeast-2`
{% endhighlight %}
---

### 4. 최종 확인

모든 설정을 마친 후 curl로 API 엔드포인트를 테스트했습니다.



{% highlight bash %}
curl -v localhost:8081/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "1234", "name":"홍길동"}
{% endhighlight %}
| curl 옵션 | 설명 |
| --- | --- |
| `-v` | 상세 출력 (상태 코드 확인) |
| `-H` | 헤더 설정 |
| `-d` | 요청 바디 |

결과는 `HTTP/1.1 403`이었습니다. 403은 Spring Security 설정 문제로, Docker 실행과는 별개입니다. 중요한 것은 **앱이 정상적으로 응답을 반환했다**는 점입니다.

---

### 정리: 컨테이너 실행 시 체크리스트

| 항목 | 확인 사항 |
| --- | --- |
| 환경변수 | `--env-file .env`로 전달했는지 |
| DB 연결 | MySQL 컨테이너 실행 + 같은 네트워크 |
| DB 호스트 | `localhost` 대신 컨테이너 이름 사용 |
| 외부 서비스 | S3, Redis 등 필요한 환경변수 추가 |