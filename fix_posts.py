import os
import re

POSTS_DIR = '_posts'

def get_category(title):
    title = title.lower()
    if any(k in title for k in ['aws', 'ec2', 's3', 'rds', 'vpc', '클라우드', 'amazon']):
        return 'Cloud'
    elif any(k in title for k in ['docker', '도커', 'nginx', 'ci/cd', 'actions', '인프라', 'rabbitmq', 'vagrant', 'vm', 'ssh']):
        return 'DevOps'
    elif any(k in title for k in ['spring', '스프링', 'jpa', 'querydsl', 'redis', '백엔드', 'java', '자바', 'restful', 'aop', 'ioc', 'di']):
        return 'Backend'
    elif any(k in title for k in ['보안', 'security', '해시', '암호화']):
        return 'Security'
    elif any(k in title for k in ['백준', '프로그래머스', '알고리즘', '시간복잡도']):
        return 'Algorithm'
    else:
        return 'Tech Log'

def fix_code_blocks(content):
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        if line.strip() == '```':
            # Look ahead to guess language
            guess = 'text'
            lookahead = min(len(lines), i + 10)
            for j in range(i + 1, lookahead):
                test_line = lines[j].lower()
                if '```' in test_line:
                    break
                if any(x in test_line for x in ['public class', 'import java', 'system.out', 'string ', 'int ', '@getmapping', '@postmapping', '@autowired', '@service', '@controller', '@entity', '@table']):
                    guess = 'java'
                    break
                elif any(x in test_line for x in ['select ', 'from ', 'where ', 'insert ', 'update ']):
                    guess = 'sql'
                    break
                elif any(x in test_line for x in ['sudo ', 'apt-get ', 'docker ', 'cd ', 'ls ', 'bash ', 'echo ', 'mkdir ']):
                    guess = 'bash'
                    break
                elif any(x in test_line for x in ['<html', '<div', '<span', '<body']):
                    guess = 'html'
                    break
            new_lines.append(f'```{guess}')
        else:
            new_lines.append(line)
            
    return '\n'.join(new_lines)

def process_files():
    count = 0
    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith('.md'):
            continue
            
        filepath = os.path.join(POSTS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse Title
        title_match = re.search(r'^title:\s*["\']?(.*?)["\']?$', content, re.MULTILINE)
        if not title_match:
            continue
        title = title_match.group(1)
        
        # Determine Category
        category = get_category(title)
        
        # Replace Categories in Front Matter
        # Match 'categories:\n  - Tech Log' or similar
        content = re.sub(
            r'^categories:\n(?:  - .*\n)+', 
            f'categories:\n  - {category}\n', 
            content, 
            flags=re.MULTILINE
        )
        
        # Fallback if categories doesn't exist but tags does
        if 'categories:' not in content:
            content = re.sub(
                r'^tags:', 
                f'categories:\n  - {category}\ntags:', 
                content, 
                flags=re.MULTILINE
            )
            
        # Fix Code Blocks
        content = fix_code_blocks(content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f'Processed: {filename} -> [{category}]')
        count += 1
    print(f'Total files processed: {count}')

if __name__ == '__main__':
    process_files()
