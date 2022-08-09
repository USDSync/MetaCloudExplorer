using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace acdt
{
    public class Resources : List<Resource> { }

    public class Resource
    {
        public string Name { get; set; }
        public string Type { get; set; }
        public string Group { get; set; }
        public string Location { get; set; }
        public string Subscription { get; set; }

        //For aggregating counts
        public int ResourceCount { get; set; }
        public float x { get; set; }
        public float y { get; set; }
        public float z { get; set; }

    }
}
