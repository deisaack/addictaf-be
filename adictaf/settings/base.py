import os
from datetime import timedelta

import raven
from decouple import Csv, config

from adictaf.aws.conf import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# LIVE_DIR = os.path.join(os.path.dirname(BASE_DIR), 'live')
LIVE_DIR = os.path.join(os.path.dirname(BASE_DIR), 'live')
SECRET_KEY=config('SECRET_KEY')

AUTH_USER_MODEL = 'users.User'
CELERY_BROKER_URL = 'amqp://localhost'
CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'TRACE',
)
CRYPTO_KEY = config('CRYPTO_KEY')
DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.postgresql_psycopg2',
        "NAME": config('DATABASE_NAME'),
        "USER": config('DATABASE_USER'),
        "PASSWORD": config('DATABASE_PASSWORD'),
        "HOST": config('HOST'),
        "PORT": '',
    }
}


DEFAULT_FROM_EMAIL = "AdictAF <"+config('EMAIL_HOST_USER')+">"
EMAIL_HOST=config('EMAIL_HOST')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_PORT=config('EMAIL_PORT')
EMAIL_USE_TLS=config('EMAIL_USE_TLS', True)
SERVER_EMAIL=config('EMAIL_HOST')

GEOIP_PATH = os.path.join(BASE_DIR, 'adictaaf/utilities/geo')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'adictaf.apps.activities',
    'adictaf.apps.core',
    'adictaf.apps.files',
    'adictaf.apps.instausers',
    'adictaf.apps.posts',
    'adictaf.apps.traffics',
    'adictaf.apps.users',
    'adictaf.utilities',
    'noire',

    'corsheaders',
    'django_ses',
    'rest_framework',
    'django_filters',
    'raven.contrib.django.raven_compat',
    'storages',

]
EXPIRY = config('JWT_EXPIRATION_DELTA', 15, cast=int)

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': timedelta(minutes=EXPIRY),
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(minutes=int(EXPIRY)),
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_AUTH_HEADER_PREFIX': 'Token',
    # 'JWT_GET_USER_SECRET_KEY': 'utilities.auth.jwt_get_secret_key',
}

LANGUAGE_CODE = 'en-us'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'adictaf.urls'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    # os.path.join(LIVE_DIR, 'static'),
    # os.path.join(LIVE_DIR, 'noire/static'),
)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
TIME_ZONE = 'Africa/Nairobi'

WSGI_APPLICATION = 'adictaf.wsgi.application'

USE_I18N = True

USE_L10N = True

USE_TZ = config('USE_TZ', False, cast=bool)

os.environ['TZ'] = TIME_ZONE

NOIRE={
    'BASE_DIR': os.path.join(LIVE_DIR, 'noire'),
    'LOG_FILE': os.path.join(LIVE_DIR, 'logs/noire.log'),
    'TIME_FORMAT': '%Y-%m-%d %H:%M:%S %Z%z',
    'API_URL': 'https://i.instagram.com/api/v1/',
    'DEVICE_SETTINTS': {
        'manufacturer': 'samsung',
        'model': 'herolte',
        'device': 'SM-G930F',
        'android_version': 23,
        'android_release': '6.0.1'
    },
    'IG_SIG_KEY': '4f8732eb9ba7d1c8e8897a75d6474d4eb3f5279137431b2aafb71fafe2abe178',
    'EXPERIMENTS': 'ig_android_disk_cache_match_journal_size_to_cache_max_count,ig_android_ad_move_carousel_indicator_to_ufi_universe,ig_android_universe_video_production,ig_android_live_follow_from_comments_universe,ig_android_ad_watchandinstall_universe,ig_android_live_analytics,ig_android_video_captions_universe,ig_android_offline_location_feed,ig_android_ontact_invite_universe,ig_android_insta_video_reconnect_viewers,ig_android_live_broadcast_blacklist,ig_android_checkbox_instead_of_button_as_follow_affordance_universe,ig_android_ufi_redesign_video_social_context,ig_android_stories_surface_universe,ig_android_verified_comments_universe,ig_android_preload_media_ahead_in_current_reel,android_instagram_prefetch_suggestions_universe,ig_android_direct_inbox_tray_suggested_user_universe,ig_android_direct_blue_tab,ig_android_light_status_bar_universe,ig_android_asset_button_new_content_animation,ig_android_async_network_tweak_universe,ig_android_react_native_lazy_modules_killswitch,ig_android_instavideo_remove_nux_comments,ig_video_copyright_whitelist,ig_android_ad_sponsor_label_story_top_design_universe,ig_android_business_action,ig_android_direct_link_style,ig_android_live_heart_enhancements_universe,ig_android_preload_item_count_in_reel_viewer_buffer,ig_android_auto_retry_post_mode,ig_android_fix_render_thread_crash,ig_android_shopping,ig_fbns_preload_default,ig_android_gesture_dismiss_reel_viewer,ig_android_ad_logger_funnel_logging_universe,ig_android_direct_links,ig_android_links_receivers,ig_android_ad_impression_backtest,ig_android_offline_freshness_toast_10_12,ig_android_invites_without_token_universe,ig_android_immersive_viewer,ig_android_mqtt_skywalker,ig_fbns_push,ig_android_react_native_universe,ig_android_special_brush,ig_android_live_consumption_abr,ig_android_story_viewer_social_context,ig_android_explore_verified_badges_stories_universe,ig_android_video_loopcount_int,ig_android_enable_main_feed_reel_tray_preloading,ig_android_ad_watchbrowse_universe,ig_android_react_native_ota,ig_android_discover_people_icon_in_others_profile,ig_android_log_mediacodec_info,ig_android_enable_back_navigation_nux_universe,ig_android_cold_start_feed_request,ig_video_use_sve_universe,ig_android_offline_explore_10_14,ig_android_stories_teach_gallery_location,ig_android_http_stack_experiment_2017,ig_android_stories_device_tilt,ig_android_pending_request_search_bar,ig_android_fb_topsearch_sgp_fork_request,ig_android_animation_perf_reporter_timeout,ig_android_new_block_flow,ig_android_direct_address_links,ig_android_share_profile_photo_to_feed_universe,ig_android_stories_private_likes,ig_android_text_background,ig_android_stories_video_prefetch_kb,ig_android_su_activity_feed,ig_android_live_stop_broadcast_on_404,ig_android_render_iframe_interval,ig_android_boomerang_entry,ig_android_camera_shortcut_universe,ig_android_fetch_fresh_viewer_list,ig_android_ad_media_url_logging_universe,ig_android_phone_confirm_rate_limit_language_universe,ig_android_keep_http_cache_on_user_switch,ig_android_facebook_twitter_profile_photos,ig_android_full_user_detail_endpoint,ig_android_direct_sqlite_universe,ig_android_family_bridge_share,ig_android_search,ig_android_insta_video_consumption_titles,ig_android_live_notification_control,ig_android_camera_universe,ig_android_instavideo_audio_only_mode,ig_android_live_video_reactions_consumption_universe,ig_android_swipe_fragment_container,ig_creation_growth_holdout,ig_android_live_save_to_camera_roll_universe,ig_android_ad_cta_redesign_universe,ig_android_sticker_region_tracking,ig_android_unified_inbox,ig_android_offline_main_feed_10_11,ig_android_chaining_teaser_animation,ig_android_business_conversion_value_prop_v2,ig_android_redirect_to_low_latency_universe,ig_android_feed_header_profile_ring_universe,ig_family_bridges_holdout_universe,ig_android_following_follower_social_context,ig_android_video_keep_screen_on,ig_android_profile_photo_as_media,ig_android_insta_video_consumption_infra,ig_android_sms_consent_in_edit_profile,ig_android_infinite_scrolling_launch,ig_in_feed_commenting,ig_android_live_broadcast_enable_year_class_2011,ig_android_direct_phone_number_links,ig_android_direct_share_sheet_ring,ig_android_stories_weblink_creation,ig_android_histogram_reporter,ig_android_network_cancellation,ig_android_react_native_insights,ig_android_insta_video_audio_encoder,ig_android_family_bridge_bookmarks,ig_android_dash_for_vod_universe,ig_android_direct_mutually_exclusive_experiment_universe,ig_android_stories_selfie_sticker,ig_android_ad_add_per_event_counter_to_logging_event,ig_android_rtl,ig_android_direct_send_auto_retry,ig_android_direct_video_autoplay_scroll,ig_android_promote_from_profile_button,ig_android_share_spinner,ig_android_profile_share_username,ig_android_sidecar_edit_screen_universe,ig_promotions_unit_in_insights_landing_page,ig_android_save_longpress_tooltip,ig_android_constrain_image_size_universe,ig_android_business_new_graphql_endpoint_universe,ig_ranking_following,ig_android_universe_reel_video_production,ig_android_sfplt,ig_android_offline_hashtag_feed,ig_android_live_skin_smooth,ig_android_stories_posting_offline_ui,ig_android_direct_add_local_thread_in_inbox,ig_android_swipe_navigation_x_angle_universe,ig_android_offline_mode_holdout,ig_android_non_square_first,ig_android_insta_video_drawing,ig_android_react_native_usertag,ig_android_swipeablefilters_universe,ig_android_analytics_logger_running_background_universe,ig_android_save_all,ig_android_reel_viewer_data_buffer_size,ig_android_disk_cache_has_sanity_check,ig_direct_quality_holdout_universe,ig_android_family_bridge_discover,ig_android_react_native_restart_after_error_universe,ig_story_tray_peek_content_universe,ig_android_profile,ig_android_high_res_upload_2,ig_android_http_service_same_thread,ig_android_remove_followers_universe,ig_android_skip_video_render,ig_android_live_viewer_comment_prompt_universe,ig_android_search_client_matching,ig_explore_netego,ig_android_boomerang_feed_attribution,ig_android_explore_story_sfslt_universe,ig_android_rendering_controls,ig_android_os_version_blocking,ig_android_encoder_width_safe_multiple_16,ig_android_direct_video_autoplay,ig_android_snippets_profile_nux,ig_android_e2e_optimization_universe,ig_android_disk_usage,ig_android_save_collections,ig_android_live_see_fewer_videos_like_this_universe,ig_android_live_view_profile_from_comments_universe,ig_formats_and_feedbacks_holdout_universe,ig_fbns_blocked,ig_android_instavideo_periodic_notif,ig_android_empty_feed_redesign,ig_android_marauder_update_frequency,ig_android_suggest_password_reset_on_oneclick_login,ig_android_live_special_codec_size_list,ig_android_enable_share_to_messenger,ig_android_live_video_reactions_creation_universe,ig_android_live_hide_viewer_nux,ig_android_channels_home,ig_android_sidecar_gallery_universe,ig_android_live_using_webrtc,ig_android_insta_video_broadcaster_infra_perf,ig_android_business_conversion_social_context,android_ig_fbns_kill_switch,ig_android_retry_story_seen_state,ig_android_react_native_universe_kill_switch,ig_android_stories_book_universe,ig_android_all_videoplayback_persisting_sound,ig_android_cache_layer_bytes_threshold,ig_android_comment_deep_linking_v1,ig_android_business_promotion,ig_android_anrwatchdog,ig_android_qp_kill_switch,ig_android_ad_always_send_ad_attribution_id_universe,ig_android_2fac,ig_direct_bypass_group_size_limit_universe,ig_android_promote_simplified_flow,ig_android_share_to_whatsapp,ig_fbns_dump_ids,ig_android_ad_show_mai_cta_loading_state_universe,ig_android_skywalker_live_event_start_end,ig_android_toplive_verified_badges_universe,ig_android_live_join_comment_ui_change,ig_android_draw_button_new_tool_animation,ig_video_max_duration_qe_preuniverse,ig_android_http_stack_kz_debug,ig_request_cache_layer,ig_android_carousel_feed_indicators_universe,ig_android_new_optic,ig_android_mark_reel_seen_on_Swipe_forward,ig_fbns_shared,ig_android_capture_slowmo_mode,ig_android_save_multi_select,ig_android_mead,ig_android_video_single_surface,ig_android_offline_reel_feed,ig_android_video_download_logging,ig_android_last_edits,ig_android_exoplayer_4142,ig_android_snippets_haptic_feedback,ig_android_gl_drawing_marks_after_undo_backing,ig_android_mark_seen_state_on_viewed_impression,ig_android_live_backgrounded_reminder_universe,ig_android_disable_comment_public_test,ig_android_user_detail_endpoint,ig_android_comment_tweaks_universe,ig_android_add_to_last_post,ig_save_insights,ig_android_live_enhanced_end_screen_universe,ig_android_ad_add_counter_to_logging_event,ig_android_sidecar,ig_android_direct_split_new_message_button,ig_android_grid_video_icon,ig_android_ad_watchandlead_universe,ig_android_progressive_jpeg,ig_android_offline_story_stickers,ig_android_direct_inbox_unseen_hint,ig_android_top_live_titles_universe,ig_android_video_prefetch_for_connectivity_type,ig_android_ad_holdout_16m5_universe,ig_android_sync_on_background_enhanced,ig_android_upload_reliability_use_fbupload_lib,ig_android_samsung_app_badging,ig_android_offline_commenting,ig_android_insta_video_abr_resize,ig_android_insta_video_sound_always_on,ig_android_disable_comment',
    'SIG_KEY_VERSION': '4',
    'MEDIA_DIR': os.path.join(LIVE_DIR, 'media/noire'),
    'STATIC_DIR': os.path.join(os.path.dirname(BASE_DIR), 'static', 'noire')
}

NOIRE['USER_AGENT'] = 'Instagram 10.26.0 Android ({android_version}/{android_release}; 640dpi; 1440x2560; {manufacturer}; {device}; {model}; samsungexynos8890; en_US)'.format(
    **NOIRE['DEVICE_SETTINTS'])



RAVEN_CONFIG = {
    'dsn': 'https://38f9bed0f04646c39c5b161e120392c3:055bd27a24d3464c90a247c95105ca37@sentry.io/1205371',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.join(BASE_DIR)),
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        'adictaf.utilities.AdictAFAdminOrReadOnly',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_PAGINATION_CLASS': 'adictaf.utilities.paginators.AdictAFPagination',
    'PAGE_SIZE': 12,
}

HEROKU = config('HEROKU', False, cast=bool)
if HEROKU:
    import dj_database_url

    db_from_env = dj_database_url.config()
    DATABASES['default'].update(db_from_env)
    DATABASES['default']['CONN_MAX_AGE'] = 500

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s|%(asctime)s|%(module)s|%(process)d|%(thread)d|%(message)s|%(name)s|%(filename)s:%(lineno)d)',
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s|%(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'sentry': {
            'level': 'ERROR', # To capture more than ERROR, change to WARNING, INFO, etc.
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'production_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LIVE_DIR, 'logs/main.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 7,
            'formatter': 'verbose',
            'filters': ['require_debug_false'],
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LIVE_DIR, 'logs/main_debug.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 7,
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
        'null': {
            "class": "logging.NullHandler",
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['null', ],
        },
        'py.warnings': {
            'handlers': ['null', ],
        },
        '': {
            'handlers': ['console', 'production_file', 'debug_file'],
            'level': "DEBUG",
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    }
}
