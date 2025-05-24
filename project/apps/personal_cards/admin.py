from django.contrib import admin

from apps.personal_cards import models


admin.site.register(models.PersonalMonthCard)
admin.site.register(models.PersonalRecommendations)
admin.site.register(models.PersonalStrength)
admin.site.register(models.SoftSkill)
admin.site.register(models.SoftSkillMark)
