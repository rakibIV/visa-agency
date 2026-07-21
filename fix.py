with open('C:\\Rakib\\Visa Agency Website\\agency\\serializers.py', 'r') as f:
    lines = f.readlines()

new_content = """            "id",
            "name",
            "email",
            "phone",
            "message",
            "target_visa",
            "target_visa_name",
            "target_country_name",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
"""
lines[240] = new_content

with open('C:\\Rakib\\Visa Agency Website\\agency\\serializers.py', 'w') as f:
    f.writelines(lines)
