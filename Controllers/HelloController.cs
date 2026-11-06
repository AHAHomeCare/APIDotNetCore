using Microsoft.AspNetCore.Mvc;
namespace ESAPAPI.Controllers
{
    [ApiController]
    [Route("[Controller]/[Action]")]
    public class HelloController :ControllerBase
    {
        [HttpGet]
        public IActionResult today()
        {
            return new JsonResult(new 
            {
                status =200,
                message ="Welcome",
                version ="1.0"
            });
        }
        [HttpGet]
        public IActionResult tomorrow()
        {
            return new JsonResult(new 
            {
                status =200,
                message ="Welcome tomorrow",
                version ="1.0"
            });
        }
        [HttpPost]
        public IActionResult nextday()
        {
            return new JsonResult(new 
            {
                status =200,
                message ="Welcome nextday",
                version ="1.0"
            });
        }
         [HttpPost]
        public IActionResult newscategory([FromBody] string key)
        {
            return new JsonResult(new 
            {
                status =200,
                message =$"Welcome nextday{key}",
                version ="1.0"
            });
        }
         

    }
}