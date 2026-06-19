<script>
	let { name, size = 20, class: klass = '', strokeWidth = 1.5, style = '' } = $props();

	const paths = {
		house: 'M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1H14v-6h-4v6H4a1 1 0 0 1-1-1V9.5z',
		sun: 'M12 3v1m0 16v1M4.22 4.22l.7.7m12.16 12.16.7.7M3 12h1m16 0h1M4.22 19.78l.7-.7M18.36 5.64l.7-.7M9 12a3 3 0 1 0 6 0 3 3 0 0 0-6 0',
		notepad:
			'M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2m-6 9h6m-6-4h6',
		play: 'M5 3l14 9-14 9V3z',
		headphones:
			'M3 18v-6a9 9 0 0 1 18 0v6M3 18a3 3 0 0 0 3 3h.75M21 18a3 3 0 0 1-3 3h-.75M18 21v-4.5M6 21v-4.5',
		chat: 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z',
		user: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
		globe:
			'M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2zm0 0c-2 4-2 8 0 12 2-4 2-8 0-12zm-9.8 7h19.6M2.2 15h19.6',
		logout: 'M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9',
		menu: 'M3 12h18M3 6h18M3 18h18',
		x: 'M18 6 6 18M6 6l12 12',
		chevronRight: 'M9 18l6-6-6-6',
		chevronLeft: 'M15 18l-6-6 6-6',
		chevronDown: 'M6 9l6 6 6-6',
		chevronUp: 'M18 15l-6-6-6 6',
		bookmark: 'M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z',
		bell: 'M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9m-4.27 13a2 2 0 0 1-3.46 0',
		search: 'M21 21l-6-6m2-5a7 7 0 1 1-14 0 7 7 0 0 1 14 0z',
		plus: 'M12 5v14M5 12h14',
		check: 'M20 6 9 17l-5-5',
		arrowRight: 'M5 12h14M12 5l7 7-7 7',
		arrowLeft: 'M19 12H5M12 19l-7-7 7-7',
		star: 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z',
		clock: 'M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2zm0 6v4l3 3',
		video:
			'M23 7l-7 5 7 5V7zM1 5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V5z',
		mic: 'M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3zm-7 9a7 7 0 0 0 14 0M12 19v4m-4 0h8',
		filter: 'M22 3H2l8 9.46V19l4 2V12.46L22 3z',
		layers: 'M12 2L2 7l10 5 10-5-10-5zm0 10L2 17l10 5 10-5-10-5z',
		spark: 'M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6L12 2z',
		eye: 'M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8zm11-3a3 3 0 1 0 0 6 3 3 0 0 0 0-6z',
		edit: 'M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z',
		moon: 'M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z',
		notepad2:
			'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm4 18H6V4h7v5h5v11zM8 13h8M8 17h5',
		share: 'M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8M16 6l-4-4-4 4M12 2v13',
		link: 'M10 13a5 5 0 0 0 7.07 0l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71M14 11a5 5 0 0 0-7.07 0l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71',
		image:
			'M3 5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5zm6 4a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm12 7l-5-5L5 21'
	};

	const d = paths[name] || paths['spark'];
</script>

<svg
	xmlns="http://www.w3.org/2000/svg"
	width={size}
	height={size}
	viewBox="0 0 24 24"
	fill="none"
	stroke="currentColor"
	stroke-width={strokeWidth}
	stroke-linecap="round"
	stroke-linejoin="round"
	class={klass}
	{style}
	aria-hidden="true"
>
	<path {d} />
</svg>
