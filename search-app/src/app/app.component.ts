import { Component } from '@angular/core';
import {HttpClient} from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'search-app';

  constructor(private http: HttpClient) { }

  tcode : string;
  submit() {
    debugger;
    return this.http.post('http://httpbin.org/post',
    JSON.stringify({qry: this.tcode})).subscribe(data => {

      console.log("POST Request is successful ", data);
      
      },
    error => {
      console.log(JSON.stringify(error.json()));
    }
    )

  }
}

