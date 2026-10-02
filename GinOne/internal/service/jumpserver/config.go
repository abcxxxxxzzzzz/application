package jumpserver

var Config = struct {
	JSURLs         []string
	SecondJumpURLs []string
}{
	JSURLs: []string{
		"https://js1.example.com",
		"https://js2.example.com",
		"https://js3.example.com",
		"https://js4.example.com",
	},

	SecondJumpURLs: []string{
		"https://gf0717.ttvmof.cn/kb/tgw/?channelCode=guanfang",
		"https://gf0717.tzssfil.cn/kb/tgw/?channelCode=guanfang",
		"https://gf0717.rdcczh.cn/kb/tgw/?channelCode=guanfang",
		"https://gf0717.pnqppv.cn/kb/tgw/?channelCode=guanfang",
	},
}