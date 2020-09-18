from __future__ import unicode_literals
import datetime
import pytz
import np
import numpy as np
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from hitcount.models import HitCount
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

from markdown_deux import markdown

from accounts.models import User
from categories.models import Category
from favourites.models import Bookmark
from locations.models import Location
from reviews.models import Review
from utility.models import Common, UrlMixin, MetaTagsMixin


class SameServices(TaggedItemBase):
    content_object = models.ForeignKey('Business', on_delete=models.PROTECT)


class Business(Common, UrlMixin, MetaTagsMixin):
    user = models.ForeignKey(User, related_name='added_by', on_delete=models.PROTECT)
    owner = models.ForeignKey(User, blank=True, null=True, related_name='owner', on_delete=models.PROTECT)
    logo = models.ImageField(upload_to="business/logos", blank=True, null=True)
    category = models.ForeignKey(Category, related_name="company", blank=True, null=True, on_delete=models.PROTECT)
    email = models.EmailField(help_text="This is required")

    website = models.URLField(blank=True, null=True, help_text="Please start with 'https://www.'")
    facebook = models.URLField(blank=True, null=True, help_text="Please leave empty if none")
    twitter = models.URLField(blank=True, null=True, help_text="Please leave empty if none")
    linkedin = models.URLField(blank=True, null=True, help_text="Please leave empty if none")
    instagram = models.URLField(blank=True, null=True, help_text="Please leave empty if none")
    youtube = models.URLField(blank=True, null=True, help_text="Please leave empty if none")

    address = models.CharField(max_length=255, blank=True, )
    location = models.ForeignKey(Location, related_name='company', blank=True, null=True,
                                 help_text="Please leave empty if 100% virtual",
                                 on_delete=models.PROTECT)
    services = TaggableManager(through=SameServices, blank=True, verbose_name='services')
    verified = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                        related_query_name='hit_count_generic_relation')

    reviews = GenericRelation(Review)
    bookmark = GenericRelation(Bookmark)

    class Meta:
        verbose_name = "biashara"
        verbose_name_plural = "biashara"

    def average_rating(self):
        all_ratings = list(map(lambda x: x.rating, self.reviews.all()))
        return np.mean(all_ratings)

    def get_absolute_url(self):
        return reverse('business:detail', kwargs={'slug': self.slug})

    def get_url_path(self):
        return reverse('business:detail', kwargs={'slug': self.slug})

    def can_edit(self, request):
        if request.user is self.owner:
            can_edit = True
            return can_edit
        elif request.user is self.user and self.owner is None:
            can_edit = True
            return can_edit
        else:
            can_edit = False
            return can_edit

    def get_markdown(self):
        description = self.description
        markdown_text = markdown(description)
        return mark_safe(markdown_text)


    @cached_property
    def image_count(self):
        return self.photos.count()

    @cached_property
    def featured_image(self):
        return self.photos.all().first()

    @cached_property
    def closed_hours(self):
        now = timezone.now()
        closed_hours = self.opening_hours.all().filter(start__gte=now, end__lte=now, weekday=now.isoweekday)
        return closed_hours
    
    @cached_property
    def closed_days(self):
        now = timezone.now()
        closed = self.opening_hours.all().filter(closed=True, weekday=now.isoweekday)
        return closed
    
    @cached_property
    def is_closed_for_now(self):
        cfn = self.closed_days or self.closed_hours
        return cfn.count()
    
    
    def is_open(self):
        now = datetime.datetime.now()
        # for open in self.opening_hours.all().filter(start__lte=now, end__gte=now, weekday=now.isoweekday):
        #     if open:
        #         return True
        is_open = self.opening_hours.all().filter(start__lte=now, end__gte=now, weekday=now.isoweekday)
        if is_open:
            return True
        else:
            return False
    #
    # @cached_property
    # def is_open_now(self):
    #     now = timezone.now()
    #     if self.is_closed_for_now:
    #         return False
    #
    #     now_time = datetime.time(now.hour, now.minute, now.second)
    #     # now_time = datetime.time()
    #     #
    #     ohs = self.opening_hours.all()
    #     for oh in ohs:
    #         is_open = False
    #         # start and end is on the same day
    #         if (oh.weekday == now.isoweekday() and oh.start <= now_time and now_time <= oh.end):
    #             is_open = oh
    #
    #         # start and end are not on the same day and we test on the start day
    #         if (oh.weekday == now.isoweekday() and
    #                 oh.start <= now_time and
    #                 ((oh.end < oh.start) and
    #                  (now_time < datetime.time(23, 59, 59)))):
    #             is_open = oh
    #
    #         # start and end are not on the same day and we test on the end day
    #         if (oh.weekday == (now.isoweekday() - 1) % 7 and
    #                 oh.start >= now_time and
    #                 oh.end >= now_time and
    #                 oh.end < oh.start):
    #             is_open = oh
    #             # print " 'Special' case after midnight", oh
    #
    #         if is_open is not False:
    #             return oh
    #     return False
    #


class BusinessImage(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='photos')
    img = models.ImageField(upload_to='business/photos', null=True)
    alt = models.CharField(max_length=256, null=True, default="photo")

    def __str__(self):
        return self.img.url

    _metadata = {
        'image': 'get_meta_image',
    }

    def get_meta_image(self):
        if self.img:
            return self.img.url
