---
layout: single
title: "Git Branch"
categories: [Github]
tag: [git, github, gitblog]
author_profile: false
sidebar:
  nav: "docs"
last_modified_at: 2024-06-26
---

# Git Branch

Branch란 독립적인 작업 공간을 만드는 기능이다.<br>
Branch는 협업에서 빠질 수 없는 깃의 기능 중 하나이다.<br>브랜치를 이해 할 때 나뭇가지를 생각하면 편하다.<br>뿌리부분(main,master)브랜치까지는 같은 커밋 역사를 공유를하다가 새로운 브랜치를 만들어주면 그때 부터는 나뭇 가지가 뻗어나가듯이 새로운 커밋 역사를 갖게 되는것이다.<br>
**만약 현재까지의 작업은 그대로 유지하면서 새로운 기능을 테스트를 하고 싶다면 어떻게 하면 좋을까?** <br>이때 새로운 브랜치를 만들어서 새로운 기능들을 테스트를 해보면된다. 만약 테스트의 성공 했다면 main브랜치에도 그 기능을 merge해주면 되고 실패했다면 main브랜치에는 그 기능을 merge를 안해주면 된다.<br>

## 협업에서 응용하기

1. main 브랜치에는 항상 가장 안정적인 버전의 코드만 두는것이 좋다.
2. main브랜치의 코드는 언제든지 배포하고 서비스할 수 있어야한다.
3. 새로운 기능을 추가하고 싶거나 버그를 수정해야할 때 새로운 브랜치에서 작업을한다.

   - 새 브랜치의 코드가 안전하다는 검증을 거친 main브랜치와 동기화(merge)한다.
   - 새 브랜치를 삭제해도 다른 브랜치에 영향이 없다.
   - 새 브랜치는 생성된 시점부터 독립적인 역사를 갖기 때문에 부담없이 push가 가능하다.

4. 브랜치 변경을 통해서 다른 팀원이 작업하고 있는 코드를 확인 할 수 있다.

## 브랜치 만들기

GitHub Desktop을 이용하여 브랜치를 쉽게 만들 수 있다.

1. Branch 메뉴에서 New Branch...버튼을 클릭하여 브랜치를 생성할 수 있다.<br>
   <img src="/images/github/branchmake.png" width="180" height="190" style="display: inline-block; margin-right: 10px;" />
   <img src="/images/github/createbranch.png" width="250" height="300" style="display: inline-block;" /><br>

2. 브랜치 목록은 Current branch탭에서 확인할 수 있다.<br>
   <img src="/images/github/currentbranch.png" width="180" height="190"/><br>
3. 새 브랜치의 history(커밋역사)를 확인해보면 main의 history와 같다는 것을 알 수 있다<br> 브랜치를 생성할 때 main의 커밋 역사를 가져오고, 그후의 역사는 독립적으로 생성된다.<br> 브랜치 목록에서 history탭을 통해 각 브랜치의 역사를 볼 수 가 있다.

   ![alt text](/images/github/history.png)

4.
