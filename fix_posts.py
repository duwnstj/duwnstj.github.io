import os
import re

POSTS_DIR = "_posts"

CATEGORIES_MAP = {
    "Cloud": ["aws", "ec2", "s3", "rds", "vpc", "cloud", "iam", "route53"],
    "DevOps": ["docker", "ci/cd", "github actions", "nginx", "haproxy", "jenkins", "github", "배포"],
    "Backend": ["spring", "java", "jpa", "backend", "백엔드", "redis"],
    "Security": ["보안", "https", "인증", "security", "jwt", "tls"],
    "TIL": ["til", "회고", "에러", "troubleshooting", "트러블슈팅"]
}

def analyze_title(title):
    title_lower = title.lower()
    categories = []
    for main_cat, keywords in CATEGORIES_MAP.items():
        if any(kw in title_lower for kw in keywords):
            categories.append(main_cat)
    
    if not categories:
        return ["Tech Log"]
    
    if "Cloud" in categories:
        return ["Cloud", "AWS"] if "aws" in title_lower else ["Cloud"]
    if "DevOps" in categories:
        return ["DevOps", "Container"] if "docker" in title_lower else ["DevOps"]
    if "Backend" in categories:
        return ["Backend", "Spring Boot"] if "spring" in title_lower else ["Backend"]
    if "Security" in categories:
        return ["Security"]
    if "TIL" in categories:
        return ["Tech Log", "TIL"]
        
    return ["Tech Log", categories[0]]

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith("---"):
        return

    parts = content.split("---", 2)
    if len(parts) < 3:
        return

    frontmatter = parts[1]
    body = parts[2]

    # Extract title
    title_match = re.search(r'^title:\s*(.+)$', frontmatter, re.MULTILINE)
    if not title_match:
        return
    title = title_match.group(1).strip("'\" ")

    # Determine categories
    cats = analyze_title(title)
    cats_str = "\n".join([f"  - {c}" for c in cats])

    # Add categories right before tags
    if "categories:" not in frontmatter:
        cat_yaml = f"categories:\n{cats_str}\n"
        if "tags:" in frontmatter:
            frontmatter = re.sub(r'(tags:)', f'{cat_yaml}\\1', frontmatter)
        else:
            frontmatter += cat_yaml

    # Fix code blocks without language tag
    # Finds lines that are exactly ``` with optional whitespace and replaces with ```text
    body = re.sub(r'^```\s*$', '```text', body, flags=re.MULTILINE)

    new_content = f"---{frontmatter}---{body}"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == "__main__":
    count = 0
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith(".md"):
            process_file(os.path.join(POSTS_DIR, filename))
            count += 1
    print(f"Successfully processed {count} markdown files.")
