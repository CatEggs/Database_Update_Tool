var casper = require('casper').create({
    pageSettings: {
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
    }
	//verbose: true,
	//logLevel: 'debug'
	
});

var x = require('casper').selectXPath;
var gRecordImages = false;



console.log('Claims Online Data Retrieval Utility. Version 1.0.0');
if(casper.cli.args.length == 0)
	casper.echo('Usage: casperjs.exe cot.js <User name> <password>').exit();

var gUserName = casper.cli.args[0];
var gPassword = casper.cli.args[1];
var gFilename = casper.cli.args[2];

//Step 1: Load the site and fill the login form
casper.start('https://ams.iclaimsonline.com/users/sign_in', function() {
	this.sendKeys("#user_email", gUserName);
	this.sendKeys("#user_password", gPassword);
	if(gRecordImages) casper.capture('ss1.png');
	console.log('Login filled..');
});


//Step 2: Submit login
casper.thenClick(x('//*[@id="new_user"]/ol/input'), function() {
	console.log('Login executed..');
});

//Step 3: Wait for site to load
casper.waitUntilVisible(x('//*[@id="search"]'), 
function() {
	console.log('Search is visible..');
},
function() {
	console.log('Search is not showing up, timeout..');
}, 4000);


//Step 4: Click on search
casper.thenClick(x('//*[@id="search"]'), function() {
	console.log('Search clicked..');
});

//Step 5: Wait for search form to appear
casper.waitUntilVisible(x('//*[@id="new_claim_search"]/fieldset[7]/li[2]/input'), 
function() {
	console.log('Search loaded..');
	if(gRecordImages) casper.capture('ss3.png');
},
function() {
	console.log('Search is not loading up, timeout..');
}, 4000);

//Step 6: Start the export process
casper.thenClick(x('//*[@id="new_claim_search"]/fieldset[7]/li[2]/input'), function() {
	console.log('Filter clicked..');
});

//Step 7: Wait for options dialog link to become available
casper.waitUntilVisible(x('//*[@id="excel_export_link"]'),
function() {
	console.log('Search results ready for export..');
	if(gRecordImages) casper.capture('ss4.png');
},
function() {
	console.log('Search results are not loading up, timeout..');
}, 4000);

//Step 8: open options dialog
casper.thenClick(x('//*[@id="excel_export_link"]'), function() {
	console.log('Export clicked..');
	if(gRecordImages) casper.capture('ss5.png');
	
});

//Step 9: wait for  bulk edit radio button to load
casper.waitUntilVisible(x('//*[@id="bulk-edit"]'), 
function () {
	console.log('Export options ready..');
	if(gRecordImages) casper.capture('ss6.png');
},
function() {
	console.log('Export options are not loading up, timeout..');
}, 4000);

//Step 10: Click on Bulk-edit
casper.thenClick(x('//*[@id="bulk-edit"]'), function() {
	console.log('Export options set..');
	if(gRecordImages) casper.capture('ss7.png');
	
});

//Step 11: Click on Process button
casper.thenClick(x('//*[@id="search_results_modal"]/footer/a[2]'), function() {
	console.log('Export executed..');
	if(gRecordImages) casper.capture('ss8.png');
});

//Step 12: wait until process results to appear
casper.waitUntilVisible(x('//*[@id="search-exports"]/li/a[2]'), 
function() {
	console.log('Results available..');
},
function() {
	console.log('Export timed out..');
}, 5000000);

//Step 13: Get the download path and download results file
casper.then(function () {
	console.log('Getting result URL..');
	var resultHolder = this.evaluate(function() {return __utils__.getElementByXPath('//*[@id="search-exports"]/li/a[2]')});
	console.log('Starting download: ' + resultHolder.href + '..');
    this.download(resultHolder.href, gFilename);
	console.log('Download finished.');
});

//Step 14: initate delete of the results from site
casper.thenClick(x('//*[@id="search-exports"]/li[1]/a[1]'), function() {
	console.log('Cleaning up..');
});

//Step 15: final wait before finishing..
casper.wait(2000, function() {
    this.echo('All done');
});






casper.run();