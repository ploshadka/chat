// export function getDomain() {
//     const url = window.location.href.split("/");
//     const domain = url[0] + "//" + url[2];
//     return `${domain}/`;
// }

export function getDomain() {
	const isDev = window.location.port === '5173';
	return isDev ? 'http://localhost:8000/' : window.location.origin + '/';
}