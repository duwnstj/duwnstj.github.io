import os
import requests
import json
from datetime import datetime

USERNAME = "duwnstj12"
POSTS_DIR = "_posts"

# _posts 폴더 생성 (Jekyll 기본 폴더)
if not os.path.exists(POSTS_DIR):
    os.makedirs(POSTS_DIR)

GRAPHQL_URL = "https://v2.velog.io/graphql"

def get_posts(username):
    slugs = []
    cursor = None
    
    while True:
        query = """
        query Posts($username: String!, $cursor: ID) {
          posts(username: $username, cursor: $cursor) {
            id
            url_slug
          }
        }
        """
        variables = {"username": username}
        if cursor:
            variables["cursor"] = cursor
            
        response = requests.post(GRAPHQL_URL, json={"query": query, "variables": variables})
        data = response.json()
        
        if 'data' not in data or not data['data']['posts']:
            break
            
        posts = data['data']['posts']
        slugs.extend([post['url_slug'] for post in posts])
        
        if len(posts) < 20:
            break
            
        cursor = posts[-1]['id']
        
    return slugs

def get_post_detail(username, url_slug):
    query = """
    query ReadPost($username: String!, $url_slug: String!) {
      post(username: $username, url_slug: $url_slug) {
        title
        released_at
        tags
        body
      }
    }
    """
    variables = {"username": username, "url_slug": url_slug}
    response = requests.post(GRAPHQL_URL, json={"query": query, "variables": variables})
    data = response.json()
    if 'data' in data and data['data']['post']:
        return data['data']['post']
    return None

def main():
    print(f"[{USERNAME}]님의 블로그 포스트를 조회합니다...")
    slugs = get_posts(USERNAME)
    print(f"총 {len(slugs)}개의 포스트를 발견했습니다.")
    
    for slug in slugs:
        post = get_post_detail(USERNAME, slug)
        if not post:
            continue
            
        title = post['title'].replace('"', '\\"')
        released_at = post['released_at']
        tags = post['tags']
        body = post['body']
        
        # 파일명 날짜 포맷팅
        date_obj = datetime.strptime(released_at[:10], "%Y-%m-%d")
        date_str = date_obj.strftime("%Y-%m-%d")
        
        # 파일명 생성
        filename = f"{date_str}-{slug}.md"
        filepath = os.path.join(POSTS_DIR, filename)
        
        # Jekyll용 머리말(Frontmatter) 생성
        tags_str = "\n".join([f"  - {tag}" for tag in tags]) if tags else ""
        
        frontmatter = f"---\nlayout: post\ntitle: \"{title}\"\ndate: {released_at}\n"
        if tags_str:
            frontmatter += f"tags:\n{tags_str}\n"
        frontmatter += "---\n\n"
        
        content = frontmatter + body
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"저장 완료: {filename}")
        
    print("모든 마이그레이션 작업이 완료되었습니다!")

if __name__ == "__main__":
    main()
