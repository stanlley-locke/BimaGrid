"""Claims admin."""

from django.contrib import admin

from .models import Claim, ClaimReview


class ClaimReviewInline(admin.TabularInline):
	model = ClaimReview
	extra = 0


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
	list_display = ("claim_number", "policy", "loss_type", "claimed_amount", "status", "created_at")
	list_filter = ("status", "loss_type")
	search_fields = ("claim_number", "policy__policy_number")
	raw_id_fields = ("policy",)
	inlines = [ClaimReviewInline]


@admin.register(ClaimReview)
class ClaimReviewAdmin(admin.ModelAdmin):
	list_display = ("claim", "decision", "reviewed_by", "created_at")
	raw_id_fields = ("claim", "reviewed_by")
