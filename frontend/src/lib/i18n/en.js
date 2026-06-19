export const en = {
	app: {
		name: 'Sanad',
		tagline: 'Your daily companion for spiritual growth',
		description: 'Learn, reflect, and ask. Deep Islamic content from trusted scholars.'
	},
	nav: {
		feed: 'Discover',
		daily: 'Today',
		posts: 'Articles',
		videos: 'Videos',
		audios: 'Listen',
		saved: 'Saved',
		profile: 'Profile',
		manage: 'Manage',
		logout: 'Sign Out',
		lightMode: 'Light mode',
		darkMode: 'Dark mode',
		primary: 'Primary navigation',
		expand: 'Expand sidebar',
		collapse: 'Collapse sidebar',
		switchLanguage: 'Switch language'
	},
	auth: {
		login: 'Sign In',
		register: 'Create Account',
		logout: 'Sign Out',
		email: 'Email',
		password: 'Password',
		username: 'Username',
		confirmPassword: 'Confirm Password',
		forgotPassword: 'Forgot password?',
		continueWithGoogle: 'Continue with Google',
		googleUnavailable: 'Google sign-in is unavailable',
		googleError: 'Could not start Google sign-in. Please try again.',
		noAccount: "Don't have an account?",
		haveAccount: 'Already have an account?',
		loginHere: 'Sign in here',
		registerHere: 'Create one here',
		emailPlaceholder: 'name@example.com',
		usernamePlaceholder: 'Your name on Sanad',
		passwordPlaceholder: 'At least 8 characters',
		loginTitle: 'Welcome back',
		loginSubtitle: 'Continue your spiritual journey',
		registerTitle: 'Join Sanad',
		registerSubtitle: 'Begin your journey with in-depth Islamic content',
		orContinue: 'or',
		backToLogin: 'Back to sign in',
		forgotTitle: 'Reset your password',
		forgotSubtitle: "Enter your email and we'll send you a reset link.",
		forgotSent: "If an account exists for that email, we've sent a reset link. Check your inbox.",
		sendResetLink: 'Send reset link',
		resetTitle: 'Choose a new password',
		resetSubtitle: 'Enter a new password for your account.',
		newPassword: 'New password',
		resetButton: 'Reset password',
		resetDone: 'Your password has been reset. You can now sign in.',
		resetInvalid: 'This reset link is invalid or has expired.',
		verifyTitle: 'Verify email',
		verifyChecking: 'Verifying your email…',
		verifyDone: 'Your email has been verified.',
		verifyFailed: 'Verification failed',
		verifyInvalid: 'This verification link is invalid or has expired.'
	},
	content: {
		type: { post: 'Post', video: 'Video', audio: 'Audio', note: 'Note', hadith: 'Hadith' },
		source: 'Reference',
		arabicText: 'Arabic Text',
		translation: 'Translation',
		save: 'Save',
		saved: 'Saved',
		markComplete: 'Mark Complete',
		completed: 'Completed',
		watchOnYoutube: 'Watch on YouTube',
		tags: 'Tags',
		comments: 'Comments',
		comment: 'Comment',
		addComment: 'Add a comment',
		noComments: 'No comments yet. Be the first.',
		commentPending: 'Thank you — your comment is awaiting approval.',
		sheikh: 'Sheikh',
		share: 'Share',
		shareThis: 'Share this',
		copyLink: 'Copy link',
		copied: 'Copied!',
		shareTargets: {
			x: 'Share on X',
			facebook: 'Share on Facebook',
			telegram: 'Share on Telegram',
			tiktok: 'Copy for TikTok'
		}
	},
	feed: {
		title: 'Discover',
		subtitle: 'Explore Islamic content',
		empty: 'No content available.',
		loadMore: 'Load More',
		filters: { all: 'All', posts: 'Posts', videos: 'Videos', audios: 'Audios', hadiths: 'Hadiths' }
	},
	daily: {
		title: 'Today',
		subtitle: 'A daily illumination for your heart',
		noContent: 'No daily guidance set for today. Browse the feed.',
		markDone: 'Mark as Done',
		guidedBy: 'Your daily guide',
		adhkar: "Today's Adhkar",
		curators: 'Curated today'
	},
	posts: {
		title: 'Articles',
		subtitle: 'Reflections and explanations',
		empty: 'No articles available.'
	},
	videos: { title: 'Videos', subtitle: 'Lectures and reminders', empty: 'No videos available.' },
	audios: {
		title: 'Listen',
		subtitle: 'Lessons and audio reflections',
		empty: 'No audios available.'
	},
	saved: {
		title: 'Saved',
		subtitle: 'Content you bookmarked',
		empty: 'Nothing saved yet. Bookmark content to find it here.'
	},
	search: {
		title: 'Search',
		placeholder: 'Search in Arabic or English…',
		noResults: 'No results for that query.',
		filters: { all: 'All', post: 'Posts', video: 'Videos', audio: 'Audios', hadith: 'Hadiths' }
	},
	profile: {
		title: 'Profile',
		bio: 'Bio',
		bioPlaceholder: 'Write a short bio…',
		nationality: 'Nationality',
		nationalityPlaceholder: 'e.g. Saudi, Egyptian…',
		editProfile: 'Edit Profile',
		saveChanges: 'Save Changes',
		stats: { completed: 'Completed', saved: 'Saved' },
		joinedOn: 'Joined',
		spiritualJournal: 'Spiritual journal',
		role: { user: 'User', content_manager: 'Content Manager', sheikh: 'Sheikh' }
	},
	manage: {
		title: 'Studio',
		subtitle: 'Moderate comments',
		noAccess: 'You do not have access to this area.',
		comments: 'Comments',
		noComments: 'No comments awaiting moderation.',
		reject: 'Reject',
		approve: 'Approve',
		create: {
			tab: 'Create Video',
			urlLabel: 'YouTube URL',
			urlPlaceholder: 'https://www.youtube.com/watch?v=…',
			urlHint: 'Paste a YouTube link to fetch the title and thumbnail.',
			invalidUrl: 'That doesn’t look like a YouTube link.',
			fetching: 'Fetching video details…',
			fetchError: 'Could not fetch video details. Check the link and try again.',
			titleLabel: 'Title',
			titlePlaceholder: 'Video title',
			descriptionLabel: 'Description',
			descriptionPlaceholder: 'Optional description or transcript excerpt…',
			categoryLabel: 'Category',
			categoryNone: '— None —',
			subcategoryLabel: 'Subcategory',
			publishNow: 'Publish immediately',
			publishHint: '(uncheck to save as draft)',
			publish: 'Publish Video',
			saveDraft: 'Save as Draft',
			submitting: 'Creating…',
			submitError: 'Failed to create video. Please try again.',
			successTitle: 'Video created!',
			successPublished: 'Published and live on the videos page.',
			successDraft: 'Saved as draft.',
			another: 'Create another',
			retry: 'Retry'
		}
	},
	admin: {
		confirm: 'Confirm',
		add: 'Add',
		tabs: {
			content: 'Content',
			daily: 'Daily',
			taxonomy: 'Taxonomy',
			comments: 'Comments',
			users: 'Users'
		},
		sectionDesc: {
			content: 'Create, edit, publish and archive content.',
			comments: 'Review and moderate user comments.',
			daily: 'Curate the daily guidance selections.',
			taxonomy: 'Manage categories, subcategories and tags.',
			users: 'Manage user roles and account status.'
		},
		open: 'Open',
		content: {
			new: 'New',
			edit: 'Edit content',
			type: 'Type',
			titleLabel: 'Title',
			body: 'Body',
			source: 'Source attribution',
			originalText: 'Original text',
			translatedText: 'Translation',
			audioFile: 'Audio file',
			featuredImage: 'Featured image',
			document: 'Document',
			published: 'Published',
			draft: 'Draft',
			archived: 'Archived',
			publish: 'Publish',
			unpublish: 'Unpublish',
			restore: 'Restore',
			search: 'Search content…'
		},
		tax: {
			categories: 'Categories',
			tags: 'Tags',
			categoryName: 'Category name',
			subName: 'Subcategory',
			tagName: 'Tag name',
			icon: 'Icon'
		},
		daily: {
			title: 'Daily Guidance',
			new: 'New entry',
			date: 'Date',
			items: 'items',
			noItems: 'No content added yet.',
			addContent: 'Add content',
			searchContent: 'Search content to add…',
			empty: 'No daily guidance entries yet.'
		},
		users: {
			search: 'Search by email or username…',
			role: 'Role',
			active: 'Active',
			inactive: 'Inactive',
			you: 'you'
		}
	},
	landing: {
		heroTitle: 'Your spiritual\njourney starts here',
		heroSubtitle:
			'In-depth Islamic content from trusted scholars. Posts, videos, hadiths, and daily guidance.',
		// Front door (/) — distinct from the learn-more hero above. A heart-and-light,
		// remembrance register; spiritual without naming any school.
		frontTitle: 'Quiet the noise,\nawaken the heart',
		frontSubtitle:
			'A calm space for remembrance, reflection, and knowledge you can trust — to soften the heart and draw it nearer, one day at a time.',
		trust: 'Knowledge from verified scholars',
		getStarted: 'Get Started',
		learnMore: 'Learn More',
		features: {
			daily: { title: 'Daily Guidance', desc: 'A hand-picked daily illumination.' },
			content: { title: 'Rich Content', desc: 'Posts, videos, audios, and hadiths.' },
			progress: { title: 'Track Progress', desc: 'Log completions and save what matters.' },
			search: { title: 'Search Everything', desc: 'Arabic and English search across all content.' }
		},
		cta: {
			title: 'Join Sanad Today',
			subtitle: 'Thousands have started their journey with us.',
			button: 'Create Free Account'
		}
	},
	learn: {
		eyebrow: 'Why Sanad',
		wisdom: 'Knowledge that benefits — for a heart that seeks.',
		trust: {
			scholars: { title: 'Verified scholars', desc: 'Every word traced to a trusted source.' },
			bilingual: { title: 'Arabic & English', desc: 'Read and search in both, seamlessly.' },
			calm: { title: 'Calm by design', desc: 'No ads, no noise — only what nourishes.' }
		},
		featuresTitle: 'Everything you need, in one place',
		featuresLede:
			'An integrated platform that pairs in-depth Islamic content with gentle tools to walk your spiritual journey.',
		contentTypes: 'Articles · Videos · Audio · Hadith',
		journeyTitle: 'A simple path',
		journeyLede: 'Three quiet steps, repeated daily.',
		steps: {
			discover: {
				title: 'Discover',
				desc: 'Browse articles, videos, audio and hadith from scholars you can trust.'
			},
			reflect: {
				title: 'Reflect',
				desc: 'Read deeply, save what moves you, and return to it any time.'
			},
			grow: { title: 'Grow', desc: 'Mark what you complete and let a daily habit take root.' }
		}
	},
	error: {
		title: 'Something went wrong',
		body: 'An unexpected error occurred. Please try again.',
		notFoundTitle: 'Page not found',
		notFoundBody: "The page you're looking for doesn't exist.",
		home: 'Go home'
	},
	upload: {
		prompt: 'Click to upload or drag an image here',
		hint: 'PNG, JPG or WebP · up to {max} MB',
		replace: 'Replace',
		remove: 'Remove image',
		newBadge: 'New',
		errorType: 'Please choose an image file.',
		errorSize: 'Image is too large (max {max} MB).'
	},
	ui: {
		loading: 'Loading…',
		error: 'Something went wrong. Please try again.',
		retry: 'Retry',
		cancel: 'Cancel',
		confirm: 'Confirm',
		close: 'Close',
		back: 'Back',
		next: 'Next',
		previous: 'Previous',
		save: 'Save',
		edit: 'Edit',
		delete: 'Delete',
		search: 'Search',
		searchPlaceholder: 'Search content…',
		noResults: 'No results found.',
		seeAll: 'See all',
		readMore: 'Read more',
		readLess: 'Show less',
		by: 'By',
		min: 'min'
	}
};
