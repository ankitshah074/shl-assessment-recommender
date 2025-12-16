
import json

# Load your current assessments
with open('shl_assessments.json', 'r', encoding='utf-8') as f:
    assessments = json.load(f)

print(f"Loaded {len(assessments)} assessments")

# Fix URLs
fixed_count = 0
for assessment in assessments:
    old_url = assessment['url']
    
    
    if '/products/product-catalog/' in old_url:
        new_url = old_url.replace('/products/product-catalog/', '/solutions/products/product-catalog/')
        assessment['url'] = new_url
        fixed_count += 1

print(f"Fixed {fixed_count} URLs")

# Save updated assessments
with open('shl_assessments.json', 'w', encoding='utf-8') as f:
    json.dump(assessments, f, indent=2, ensure_ascii=False)

print("✓ Saved updated assessments")

# Verify
print("\nSample URLs after fix:")
for i, assessment in enumerate(assessments[:3], 1):
    print(f"{i}. {assessment['url']}")

print("\n✓ URLs fixed! Now run evaluation again.")