#include<bits/stdc++.h>
using namespace std;

int main(){
    int n;
    vector<int> vec(n);
    cin >> n;
    long long sum = 0;
    for(int i = 0; i < n; i++){
        int a;
        cin >> a;
        sum += a;
    }
    cout << sum << endl;
}