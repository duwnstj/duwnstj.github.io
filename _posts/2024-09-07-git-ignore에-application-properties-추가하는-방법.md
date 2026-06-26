---
layout: post
title: "git ignore에 application properties 추가하는 방법"
date: 2024-09-07T13:06:01.270Z
categories:
  - Tech Log
tags:
  - Spring
---

# 왜 application.properties 파일을 보호해야할까?
- `application.properties` 파일에는 환경 설정 정보 뿐만 아니라, 데이터 베이스의 비밀번호 ,API 키 , JWT 시크릿 키 등 중요한 민감한 정보가 포함될 수 있다. 이러한 정보가 깃허브와 같은 공개된 저장소에 노출되면 , 보안 위협이 발생할 수 있다. 따라서 이를 git에 커밋하지 않도록 설정하는것이 필수적이라 할 수 있다.

## .gitignore의 역할
- `gitignore` 파일은 깃에서 버전 관리하지 않아야할 파일이나 폴더를 지정할 수 있다. 이 블로그글에서는 `application.properties 파일을 .gitignore`에 추가하여 보안 정보를 깃허브에 올리지 않는 방법을 설명하겠다.

## .gitignore에 application.properties 추가 방법

`git ignore` 파일에 들어가서 application.properties 파일을 넣어주면 된다. 
**그렇게 하고 나서 꼭 Gradle을 다시 build를 해주어야한다.** build를 해주지 않는다면 `application properties`가 `gitignore`에 제대로 적용이 안된다.
![](https://velog.velcdn.com/images/duwnstj12/post/e18cd12b-0512-48ac-86b7-af95a3e1c4cf/image.png)
![](https://velog.velcdn.com/images/duwnstj12/post/3b0b7f8d-6558-43a8-b753-530eb8bd0e7c/image.png)

## 이미 application.properties 파일을 github에 올렸다면?
만약 이미 `application.properties` 파일을 Github에 커밋한 경우, Git Bash에서 아래 명령어를 사용하여 파일을 Git에서 제거할 수 있다. 

> 명령어 : git rm --cached <관리하지 않고자하는 파일의 경로>

1. 위 명령어로 파일을 제거한다.
2. `git status` 명령어로 파일이 삭제된 것을 확인한 후, 변경 사항을 푸시한다.
이제 `application.properties` 파일은 더이상 Git에서 추적도지 않으면서 이 후 변경 사항도 GitHub에 업로드 되지 않는다.

## 환경 변수를 활용한 민감한 정보 보호 
이렇게 git ignore에 application.properties 파일을 설정하는 방법도 있지만 더 많이 쓰이는 방식은 환경 변수를 설정해주는것이다. 

### 환경 변수 설정 하는 법
1. **application.properties**에 환경 변수 명을 설정해준다.
![](https://velog.velcdn.com/images/duwnstj12/post/e7618f03-6fb8-4a1c-878c-33f7c6197428/image.png)

2. **Edit Configulation**을 클릭한다.
![](https://velog.velcdn.com/images/duwnstj12/post/8c9a3d2d-02f0-4151-80fe-ff8358904d4b/image.png)

3. **Modify Options**를 클릭한 후 , **Environment variables** 옵션을 선택한다.
![](https://velog.velcdn.com/images/duwnstj12/post/79002970-127f-496e-a896-c93b9abe3f90/image.png)

![](https://velog.velcdn.com/images/duwnstj12/post/a617b0a3-cbf7-46d1-95d7-768381f961ad/image.png)

4. 환경 변수를 입력할 수 있는 창이 나타나면, 오른쪽의 **Edit Environment Variables** 버튼을 클릭한다.
![](https://velog.velcdn.com/images/duwnstj12/post/38168006-e395-40ba-a9bd-1941150737d3/image.png)
5. 새로운 창에서 , `application.properties`파일에서 사용하는 환경 변수 이름을 **Key**로 , 그 값을 **Value**에 입력해준다.
![](https://velog.velcdn.com/images/duwnstj12/post/3617ea2a-650b-43ba-9195-30e74993a956/image.png)

이렇게 환경 변수를 사용해 민감한 데이터가 깃헙에 올라가는것을 방지할 수 있다.