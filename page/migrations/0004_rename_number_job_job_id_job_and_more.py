# Generated by Django 5.1.2 on 2024-11-11 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0003_job_machine_probleme_machine_number_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='number_job',
            new_name='ID_job',
        ),
        migrations.AlterUniqueTogether(
            name='jobmachine',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='job',
            name='r',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='jobmachine',
            name='ID_machine',
            field=models.IntegerField(default=1, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='job',
            name='d',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='probleme',
            name='CONSTRAINT',
            field=models.CharField(blank=True, choices=[(None, 'Aucune contrainte'), ('delivery', 'Date de livraison'), ('prep_time', 'Temps de préparation'), ('no_wait', 'no wait'), ('no_idle', 'no idele')], max_length=20, null=True, verbose_name='Contrainte'),
        ),
        migrations.RemoveField(
            model_name='jobmachine',
            name='machine',
        ),
        migrations.RemoveField(
            model_name='jobmachine',
            name='job',
        ),
        migrations.DeleteModel(
            name='Machine',
        ),
        migrations.AddField(
            model_name='jobmachine',
            name='job',
            field=models.ManyToManyField(to='page.job'),
        ),
    ]
