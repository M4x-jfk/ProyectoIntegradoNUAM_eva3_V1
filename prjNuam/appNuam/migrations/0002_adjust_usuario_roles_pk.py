from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appNuam', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE usuario_roles DROP PRIMARY KEY;
                ALTER TABLE usuario_roles
                    ADD COLUMN id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;
                ALTER TABLE usuario_roles
                    ADD UNIQUE KEY uniq_usuario_roles (usuario_id, rol_id);
            """,
            reverse_sql="""
                ALTER TABLE usuario_roles DROP INDEX uniq_usuario_roles;
                ALTER TABLE usuario_roles DROP COLUMN id;
                ALTER TABLE usuario_roles ADD PRIMARY KEY (usuario_id, rol_id);
            """,
        ),
    ]
