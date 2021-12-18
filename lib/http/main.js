class Http {
    constructor(url, method, headers, body) {
        this.url = url;
        this.method = method;
        this.headers = headers;
        this.body = "<html><body>Hello World</body></html>";
    }
    post() {
        console.log(this.body.name);
    }
}

let http = new Http('www.google.com', 'GET', {}, { name: 'John' });
http.post();