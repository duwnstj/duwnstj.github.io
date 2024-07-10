---
layout: single
title: "Git Branch,PullRequest"
categories: [Github]
tag: [git, github, gitblog]
author_profile: false
sidebar:
  nav: "docs"
last_modified_at: 2024-06-26
---

# Git Branch

Branch란 독립적인 작업 공간을 만드는 기능이다.<br>
Branch는 협업에서 빠질 수 없는 깃의 기능 중 하나이다.<br>
브랜치를 이해할 때 나뭇가지를 생각하면 편하다.<br>
뿌리 부분(main, master) 브랜치까지는 같은 커밋 역사를 공유하다가 새로운 브랜치를 만들면 그때부터는 나뭇가지가 뻗어나가듯이 새로운 커밋 역사를 갖게 되는 것이다.<br>
**만약 현재까지의 작업은 그대로 유지하면서 새로운 기능을 테스트하고 싶다면 어떻게 하면 좋을까?**<br>
이때 새로운 브랜치를 만들어서 새로운 기능들을 테스트해보면 된다. 만약 테스트에 성공했다면 main 브랜치에도 그 기능을 merge해주면 되고, 실패했다면 main 브랜치에는 그 기능을 merge하지 않으면 된다.<br>

## 협업에서 응용하기

1. **main 브랜치에는 항상 가장 안정적인 버전의 코드만 두는 것이 좋다.**
2. **main 브랜치의 코드는 언제든지 배포하고 서비스할 수 있어야 한다.**
3. **새로운 기능을 추가하거나 버그를 수정할 때는 새로운 브랜치에서 작업한다.**
   - 새 브랜치의 코드가 안전하다는 검증을 거친 후 main 브랜치와 동기화(merge)한다.
   - 새 브랜치를 삭제해도 다른 브랜치에 영향이 없다.
   - 새 브랜치는 생성된 시점부터 독립적인 역사를 갖기 때문에 부담 없이 push가 가능하다.
4. **브랜치 변경을 통해 다른 팀원이 작업하고 있는 코드를 확인할 수 있다.**

## 브랜치 만들기

GitHub Desktop을 이용하여 브랜치를 쉽게 만들 수 있다.

1. **Branch 메뉴에서 New Branch... 버튼을 클릭하여 브랜치를 생성할 수 있다.**<br>
   <img src="/images/github/branchmake.png" width="180" height="190" style="display: inline-block; margin-right: 10px;" />
   <img src="/images/github/createbranch.png" width="250" height="300" style="display: inline-block;" /><br>

2. **브랜치 목록은 Current branch 탭에서 확인할 수 있다.**<br>
   <img src="/images/github/currentbranch.png" width="180" height="190"/><br>
3. **새 브랜치의 history(커밋 역사)를 확인해보면 main의 history와 같다는 것을 알 수 있다.**<br>
   브랜치를 생성할 때 main의 커밋 역사를 가져오고, 그 후의 역사는 독립적으로 생성된다.<br>
   브랜치 목록에서 history 탭을 통해 각 브랜치의 역사를 볼 수 있다.

   ![alt text](/images/github/history.png)

## 브랜치 전환

브랜치 생성 후 현재 작업 중인 브랜치를 전환할 수 있다.<br>
GitHub Desktop을 이용하여 바꿔보자.

- **Current branch 탭에서 브랜치를 스왑할 수 있다.**<br>
  <img src="/images/github/브랜치.png" width="200" height="210" /><br>
- **브랜치를 전환하면 파일 상태도 해당 브랜치의 커밋에 맞게 변경된다.**<br>
  한마디로 같은 디렉토리(폴더)에서 작업을 하고 있더라도 브랜치가 다르면 서로 다른 상태의 파일을 가지고 있다고 생각하면 된다.

## 브랜치 publish

브랜치를 생성하면 로컬에는 새 브랜치가 생성되지만, 원격에는 아직 생성되지 않는다.<br>
그래서 우리는 GitHub에 브랜치를 push해야 하는데, 브랜치를 push하는 것을 Git에서는 브랜치를 공개한다는 의미로 publish라고 한다.<br>
이렇게 원격 저장소에 publish를 하게 되면 같은 프로젝트를 진행하고 있는 다른 사람들에게도 이 브랜치가 보이게 된다.

## 브랜치와 HEAD

각 커밋은 이전 커밋(부모 커밋)의 정보를 지니고 있다.<br>
특정 커밋에서 시작해서 하나씩 거슬러 올라가면 최초의 커밋까지 찾아갈 수 있다.<br>
따라서 브랜치는 하나의 커밋을 통해 최초부터 해당 커밋까지의 모든 역사를 파악할 수 있다.<br>
브랜치와 HEAD는 모두 특정 커밋 하나를 가리키고 있다.<br>
브랜치는 특정 커밋을 가리키고 있다.<br>
HEAD는 현재 작업 중인 커밋을 가리키고 있다.

## merge

merge란 서로 다른 브랜치의 커밋 역사를 합치는 기능을 말한다.

### merge의 특징

현재 작업하고 있는 브랜치와 merge를 할 브랜치 두 개를 갖는다. 각 브랜치를 A, B라고 생각해보자.<br>
현재 작업하고 있는 브랜치(HEAD)에서 merge할 브랜치와 성공적으로 merge가 되면 HEAD 브랜치에 새로운 merge 커밋이 생기게 된다.<br>
merge 커밋과 일반 커밋의 차이점은 부모 커밋의 개수가 다르다는 것이다. merge 커밋은 부모 커밋의 개수가 2개이고, 일반 커밋은 부모 커밋의 개수가 하나이다.<br>
merge가 성공적으로 이루어지면 HEAD 브랜치(A)에 merge할 브랜치(B)의 변경 사항이 적용된다.

이렇게 반영된 두 개의 브랜치 변경 사항을 main에 적용시키려면 어떻게 해야 할까?

먼저 현재 브랜치(HEAD)를 main 브랜치로 변경해주고 아까 merge를 한 브랜치(A)를 똑같이 merge해주면 된다.<br>
이렇게 merge가 성공적으로 이뤄지면 A, B 브랜치의 변경 사항이 모두 main 브랜치에 반영된다.

## merge하기

### 1. GitHub Desktop에서의 merge 과정

- **merge 커밋을 생성할 브랜치로 전환한다.**<br>
  Branch 메뉴에 있는 Merge into Current Branch...를 선택한다.<br><br>
  <img src="/images/github/merge.png" width="200" height="210" /><br>
- **merge 할 브랜치를 선택한다.**<br>
  Create a merge commit 버튼을 클릭하여 새로운 merge 커밋을 생성한다.<br><br>
  <img src="/images/github/merge선택.png" width="400" height="210" /><br>

- **만약 충돌이 발생해서 merge를 할 수 없다면, 먼저 파일을 적절하게 편집해서 충돌을 해결한다.**

### 2. 브랜치 삭제

- **더 이상 필요 없는 브랜치는 삭제할 수 있다.**<br>
  Branch 메뉴에 있는 Delete... 버튼을 누르고 삭제할 브랜치를 선택한다.<br>
  원격 저장소에도 브랜치가 있다면 동시에 원격 저장소에서도 삭제할 수 있다.<br>
  브랜치 삭제는 되돌릴 수 없다. 따라서 신중하게 결정해야 한다.

## Pull Request(PR)

브랜치의 merge 여부를 팀원들끼리 확인하고 결정할 수 있다.<br>
코드 변경 내용을 쉽게 확인 가능하고 리뷰를 작성할 수 있어서 협업에서 필수적이다.<br>
브랜치 간의 merge 충돌이 일어나도 PR을 생성할 수 있지만 충돌을 해결하기 전에는 merge(병합)을 할 수 없다.

### PR(Pull Request) 생성 과정

- **GitHub에서 Pull request 탭의 New pull request 또는 New 버튼을 클릭한다.**<br>
  <img src="/images/github/pr생성.png" width="400" height="210" /><br>
- **base 브랜치에는 변경 사항을 반영할 브랜치를, compare 브랜치에는 변경 사항이 있는 브랜치를 선택한다.**<br>
  브랜치에서 어떤 변경이 있었는지 팀원들이 알아보기 쉽게 설명을 작성해준다.<br>
  Create pull request를 클릭하여 PR을 생성한다.<br>
  <img src="/images/github/prcreate.png" width="400" height="210" /><br>

---

출처 : [Git과 GitHub(코드밸리)](https://www.codingvalley.com/course/clptd3p153c6e0b121337325v)의 강의
