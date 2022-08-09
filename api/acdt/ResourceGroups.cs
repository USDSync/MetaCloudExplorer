using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace acdt
{
    public class ResourceGroups : List<ResourceGroup> { }

    public class ResourceGroup
    {
        public string Name { get; set; }
        public string Subscription { get; set; }
        public string Location { get; set; }

        public int ResourceCount { get; set; }
        public float x { get; set; }
        public float y { get; set; }
        public float z { get; set; }


    }
}
