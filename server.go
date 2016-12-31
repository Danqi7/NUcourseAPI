package main

import (
	"fmt"
	"bytes"
	//"golang.org/x/net/html"
	//"io/ioutil"
	"log"
	"net/http"
	"github.com/PuerkitoBio/goquery"
)

// given "MUSIC/index.html", return full url for that href
// input url in format of "...../index.html"
func getFullLink(href string, url string) string {
	url = url[:len(url)-len("index.html")]

	var buffer bytes.Buffer
    buffer.WriteString(url)
	buffer.WriteString(href)

	return buffer.String()
}

//crawl the url and extract the href and text of <a> for each <li>
func crawl(url string, chHref chan string, chText chan string, chFinished chan bool) {
	resp, err := http.Get(url)

	defer func() {
		//notify that we'are done crawling
		chFinished <- true
	}()

	if err != nil {
		log.Printf("Error crawling the url %s while getting all schools", url)
	}
	defer resp.Body.Close()

	doc, err := goquery.NewDocumentFromResponse(resp)
	if err != nil {
		log.Fatal("A wild error has occured while parsing the response html: %s", err);
	}

	doc.Find("li").Each(func (i int, s *goquery.Selection) {
		title := s.Find("a").Text()
		chText <- title
		link, exist := s.Find("a").Attr("href")
		if (exist == true) {
			chHref <- link
		}
	})
}

func getAllDepartments() {
	url := "http://www.northwestern.edu/class-descriptions/4650/index.html"
	urls := getAllSchools(url)
	log.Println(urls)

	//channels
	chHref := make(chan string)
	chText := make(chan string)
	chFinished := make(chan bool)

	hrefs := make([]string, 0)
	texts := make([]string, 0)

	for _, url := range urls {
		go crawl(url, chHref, chText, chFinished)
	}

	//subscribe to the three channels
	for c:= 0; c < len(urls);{
		select {
		case href := <-chHref:
			hrefs = append(hrefs, href)
		case text := <-chText:
			texts = append(texts, text)
		case <-chFinished:
			c++
		}
	}

	log.Println(hrefs)
	log.Println(texts)
}

// return a list of school urls
func getAllSchools(url string) []string {
	resp, err := http.Get(url)
	if err != nil {
		log.Printf("Error crawling the url %s while getting all schools", url)
	}
	// bytes, err1 := ioutil.ReadAll(resp.Body)
	// if err1 != nil {
	// 	log.Printf("Error reading response")
	// }
	defer resp.Body.Close()

	urls := make([]string, 0)

	doc, err3 := goquery.NewDocumentFromResponse(resp)
	if err3 != nil {
		log.Fatal("A wild error has occured while parsing the response html: %s", err3);
	}
	doc.Find("li").Each(func (i int, s *goquery.Selection) {
		log.Println(i)
		title := s.Find("a").Text()
		link, exist := s.Find("a").Attr("href")
		if (exist == true) {
			// log.Println(link)
			urls = append(urls, link)
		}
		log.Println(title)
	})
	// log.Println(urls)

	for i, url1 := range urls {
		urls[i] = getFullLink(url1, url)
	}
	return urls
}

func handleSchools(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hi %s", r.URL.Path[1:])
	log.Println(r.URL)
	// url := "http://www.northwestern.edu/class-descriptions/4650/index.html"
	// getAllSchools(url)
	getAllDepartments()
}

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hi %s", r.URL.Path[1:])
	log.Println(r.URL)
}

func main() {
	http.HandleFunc("/api/schools", handleSchools)
	http.HandleFunc("/", handler)
	log.Println("Server started at http://localhost:5050")
	log.Fatal(http.ListenAndServe(":5050", nil))
}
