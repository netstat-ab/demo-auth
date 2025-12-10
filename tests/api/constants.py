from datetime import datetime

PASSWORD_POLICY_MIN_LENGTH = 8
PASSWORD_POLICY_MAX_LENGTH = 10

# Код регистрации, отсутствующий в базе
NEW_REGISTRATION_CODE = 'NEW_REGISTRATION_CODE'

# Код регистрации, привязанный к пользователю с адресом электронной почты USER_2_EMAIL
USER_2_REGISTRATION_CODE = 'USER_2_REGISTRATION_CODE'

# Текущее время для freezetime
NOW = datetime.fromisoformat('2025-10-23T12:34:56.789012+03:00')

# Пользователя с данным адресом электронной почты не существует
NOT_EXISTING_USER_EMAIL = 'new_user@example.org'

# email существующего пользователя, адрес электронной почты не подтвержден, запись о регистрации отсутствует
USER_1_EMAIL = 'user1@example.org'

# email существующего пользователя, адрес электронной почты не подтвержден, запись о регистрации существует
USER_2_EMAIL = 'user2@example.org'

# email существующего пользователя, с подтвержденным адресом электронной почты
USER_3_EMAIL = 'user3@example.org'
